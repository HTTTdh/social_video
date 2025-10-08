import httpx
from typing import Optional, Tuple, List, Union, Dict
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.repositories import channel_repo
from app.schemas.common import ChannelPlatformEnum as PF

class InstagramService:
    def __init__(self):
        self.settings = get_settings()
        self.graph_v = getattr(self.settings, "GRAPH_API_VERSION", "v19.0")
        self.base_url = f"https://graph.facebook.com/{self.graph_v}"

    def get_login_url(self, redirect_uri: str) -> str:
        """Instagram sử dụng Facebook OAuth"""
        app_id = self.settings.FACEBOOK_APP_ID
        if not app_id:
            raise ValueError("FACEBOOK_APP_ID not configured")
        scope = "instagram_basic,instagram_content_publish"
        return f"https://www.facebook.com/{self.graph_v}/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={scope}"

    async def get_instagram_accounts(self, user_access_token: str) -> List[Dict]:
        """Lấy Instagram business accounts (async, tránh blocking)"""
        async with httpx.AsyncClient(timeout=30) as client:
            pages_url = f"{self.base_url}/me/accounts"
            pr = await client.get(pages_url, params={"access_token": user_access_token})
            try:
                pages = pr.json().get("data", [])
            except Exception:
                pages = []
            instagram_accounts: List[Dict] = []
            for page in pages:
                ig_url = f"{self.base_url}/{page['id']}"
                ir = await client.get(ig_url, params={
                    "fields": "instagram_business_account",
                    "access_token": page.get("access_token"),
                })
                try:
                    j = ir.json()
                except Exception:
                    j = {}
                if "instagram_business_account" in j:
                    instagram_accounts.append({
                        "page_id": page["id"],
                        "instagram_id": j["instagram_business_account"]["id"],
                        "access_token": page.get("access_token"),
                    })
        return instagram_accounts
    
    async def post_to_instagram(self, instagram_id: str, access_token: str, image_url: str, caption: str) -> Dict:
        """Đăng ảnh lên Instagram (async)"""
        async with httpx.AsyncClient(timeout=60) as client:
            create_url = f"https://graph.facebook.com/{self.graph_v}/{instagram_id}/media"
            create_resp = await client.post(create_url, data={
                "image_url": image_url,
                "caption": caption,
                "access_token": access_token,
            })
            try:
                cj = create_resp.json()
            except Exception:
                cj = {"raw": create_resp.text}
            if create_resp.status_code >= 400 or not cj.get("id"):
                return {"success": False, "status": create_resp.status_code, "error": cj}
            media_id = cj["id"]
            publish_url = f"https://graph.facebook.com/{self.graph_v}/{instagram_id}/media_publish"
            publish_resp = await client.post(publish_url, data={
                "creation_id": media_id,
                "access_token": access_token,
            })
            try:
                pj = publish_resp.json()
            except Exception:
                pj = {"raw": publish_resp.text}
            if publish_resp.status_code >= 400:
                return {"success": False, "status": publish_resp.status_code, "error": pj}
            return {"success": True, "id": pj.get("id")}
        
    def get_channel_token_and_igid(self, db: Session, channel_id: int) -> Tuple[Optional[str], Optional[str]]:
        ch = channel_repo.get_by_id(db, channel_id)
        if not ch:
            return None, None
        plat = getattr(ch.platform, "value", ch.platform)
        if plat != PF.instagram.value or not getattr(ch, "access_token", None):
            return None, None
        return getattr(ch, "access_token", None), getattr(ch, "external_id", None)

    async def create_media_container(self, token: str, ig_id: str, **kwargs) -> Tuple[bool, Union[str, dict]]:
        """
        Trả (ok, result):
            - ok=True  -> result = creation_id (str)
            - ok=False -> result = {status, error|raw}
        """
        if not token or not ig_id:
            return False, {"status": 400, "error": "Missing token or ig_id"}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"https://graph.facebook.com/{self.graph_v}/{ig_id}/media",
                params={"access_token": token},
                data=kwargs,
            )
        # parse an toàn
        try:
            body = r.json()
        except Exception:
            body = {"raw": r.text}

        if r.status_code >= 400:
            return False, {"status": r.status_code, "error": body.get("error") or body}

        cid = body.get("id")
        if not cid:
            # FB trả 200 nhưng không có 'id' (hiếm) -> vẫn coi là lỗi để bạn biết nội dung
            return False, {"status": r.status_code, "error": body}
        return True, cid

    async def publish_container(self, token: str, ig_id: str, creation_id: str) -> dict:
        if not token or not ig_id or not creation_id:
            return {"success": False, "status": 400, "error": "Missing token/ig_id/creation_id"}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"https://graph.facebook.com/{self.graph_v}/{ig_id}/media_publish",
                params={"access_token": token},
                data={"creation_id": creation_id},
            )
        try:
            body = r.json()
        except Exception:
            body = {"raw": r.text}
        if r.status_code >= 400:
            return {"success": False, "status": r.status_code, "error": body.get("error") or body}
        return {"success": True, "id": body.get("id")}

    async def post_photo(self, token: str, ig_id: str, image_url: str, caption: Optional[str]):
        if not token or not ig_id:
            return {"success": False, "status": 400, "error": "Missing token or ig_id"}
        ok, res = await self.create_media_container(token, ig_id, image_url=image_url, caption=caption or "")
        if not ok:
            return {"success": False, **res}
        return await self.publish_container(token, ig_id, res)

    async def post_video(self, token: str, ig_id: str, video_url: str, caption: Optional[str], is_reel: bool = True):
        if not token or not ig_id:
            return {"success": False, "status": 400, "error": "Missing token or ig_id"}
        params = {"video_url": video_url, "caption": caption or ""}
        if is_reel:
            params["media_type"] = "REELS"
        ok, res = await self.create_media_container(token, ig_id, **params)
        if not ok:
            return {"success": False, **res}
        return await self.publish_container(token, ig_id, res)

    async def post_carousel(self, token: str, ig_id: str, image_urls: List[str], caption: Optional[str]):
        if not token or not ig_id:
            return {"success": False, "status": 400, "error": "Missing token or ig_id"}
        child_ids: List[str] = []
        for u in image_urls:
            ok, res = await self.create_media_container(token, ig_id, image_url=u, is_carousel_item="true")
            if not ok:
                return {"success": False, **res}
            child_ids.append(res)
        ok, parent = await self.create_media_container(
            token, ig_id, caption=caption or "", children=",".join(child_ids), media_type="CAROUSEL"
        )
        if not ok:
            return {"success": False, **parent}
        return await self.publish_container(token, ig_id, parent)

from typing import Optional, Dict
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx, os, secrets, base64, hashlib, time, urllib.parse as url
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.repositories import channel_repo
from dotenv import load_dotenv, find_dotenv

router = APIRouter(prefix="/oauth", tags=["oauth"])

# CONFIG
load_dotenv(find_dotenv(), override=True)

OAUTH_CFG: Dict[str, Dict] = {
    "facebook": {
        "auth_url": "https://www.facebook.com/v23.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v23.0/oauth/access_token",
        "client_id": os.getenv("FB_APP_ID"),
        "client_secret": os.getenv("FB_APP_SECRET"),
        "redirect_uri": os.getenv("FB_REDIRECT_URI"),
        "scope": (
            "pages_show_list,pages_manage_posts,pages_read_engagement,"
            "pages_manage_metadata,instagram_basic,instagram_content_publish"
        ),
        "use_pkce": False,
    },
    "tiktok": {
        "auth_url": "https://www.tiktok.com/v2/auth/authorize/",
        "token_url": "https://open.tiktokapis.com/v2/oauth/token/",
        "client_id": os.getenv("TIKTOK_CLIENT_KEY"),
        "client_secret": os.getenv("TIKTOK_CLIENT_SECRET"),
        "redirect_uri": os.getenv("TIKTOK_REDIRECT_URI"),
        "scope": "user.info.basic,video.upload,video.publish",
        "use_pkce": False,
    },
    "youtube": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "redirect_uri": os.getenv("YOUTUBE_REDIRECT_URI"),
        "scope": "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly",
        "use_pkce": True,
    },
}

STATE_MEM: Dict[str, Dict] = {}
STATE_TTL = 600  # giây

# HELPERS

def _pkce_pair():
    v = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip("=")
    c = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).decode().rstrip("=")
    return v, c

def _validate_cfg_or_400(provider: str, cfg: Dict):
    missing = [k for k in ("client_id", "redirect_uri") if not cfg.get(k)]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing OAuth config for {provider}: {', '.join(missing)}"
        )
    # Google: http chỉ chấp nhận localhost; còn lại phải https
    if provider == "youtube":
        ru = (cfg.get("redirect_uri") or "").strip()
        if ru.startswith("http://") and not (ru.startswith("http://localhost") or ru.startswith("http://127.0.0.1")):
            raise HTTPException(
                400,
                detail="YOUTUBE_REDIRECT_URI phải là http://localhost... (dev) hoặc HTTPS domain (prod)."
            )

def _clean_expired_states():
    now = time.time()
    for k in list(STATE_MEM.keys()):
        if now - STATE_MEM[k].get("ts", 0) > STATE_TTL:
            STATE_MEM.pop(k, None)


@router.get("/{provider}/start")
async def oauth_start(provider: str):
    cfg = OAUTH_CFG.get(provider)
    if not cfg:
        raise HTTPException(404, "Provider not supported")
    _validate_cfg_or_400(provider, cfg)

    _clean_expired_states()
    state = secrets.token_urlsafe(24)

    params = {
        "response_type": "code",
        "redirect_uri": cfg["redirect_uri"],
        "scope": cfg["scope"],
        "state": state,
    }
    if provider == "tiktok":
        params["client_key"] = cfg["client_id"]
    else:
        params["client_id"] = cfg["client_id"]

    if provider == "youtube":
        params["access_type"] = "offline"
        params["prompt"] = "consent"
        params["include_granted_scopes"] = "true"

    if cfg["use_pkce"]:
        verifier, challenge = _pkce_pair()
        STATE_MEM[state] = {"verifier": verifier, "provider": provider, "ts": time.time()}
        params["code_challenge"] = challenge
        params["code_challenge_method"] = "S256"
    else:
        STATE_MEM[state] = {"provider": provider, "ts": time.time()}

    url_auth = f'{cfg["auth_url"]}?{url.urlencode(params)}'
    # print(f"[OAUTH START] {provider}: {url_auth}")  # bật nếu cần debug
    return RedirectResponse(url_auth)

@router.get("/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db),
):
    if not code or not state:
        return HTMLResponse(
            "<h3>Callback thiếu code/state.</h3>"
            "<p>Kiểm tra lại redirect_uri đã khai báo trên console và URL tạo ở /start.</p>",
            status_code=400,
        )

    rec = STATE_MEM.pop(state, None)
    if not rec or rec.get("provider") != provider or (time.time() - rec.get("ts", 0)) > STATE_TTL:
        return HTMLResponse("<h3>State không hợp lệ hoặc đã hết hạn.</h3>", status_code=400)

    cfg = OAUTH_CFG.get(provider)
    if not cfg:
        raise HTTPException(404, "Provider not supported")
    _validate_cfg_or_400(provider, cfg)

    # ===== đổi code -> token =====
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if provider == "facebook":
                # Facebook yêu cầu GET
                q = {
                    "client_id": cfg["client_id"],
                    "client_secret": cfg["client_secret"],
                    "redirect_uri": cfg["redirect_uri"],
                    "code": code,
                }
                token_res = await client.get(cfg["token_url"], params=q)
            else:
                data = {
                    "grant_type": "authorization_code",
                    "redirect_uri": cfg["redirect_uri"],
                    "code": code,
                }
                if provider == "tiktok":
                    data["client_key"] = cfg["client_id"]
                    data["client_secret"] = cfg["client_secret"]
                else:  # youtube
                    data["client_id"] = cfg["client_id"]
                    data["client_secret"] = cfg["client_secret"]
                if cfg["use_pkce"]:
                    data["code_verifier"] = rec.get("verifier")

                token_res = await client.post(
                    cfg["token_url"],
                    data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
    except Exception as ex:
        return HTMLResponse(f"<h3>Lỗi gọi token endpoint:</h3><pre>{ex}</pre>", status_code=500)

    if token_res.status_code >= 400:
        body = token_res.text
        html = f"""
        <h3>OAuth {provider} thất bại (token exchange)</h3>
        <pre style="white-space:pre-wrap">{body}</pre>
        <script>
          if (window.opener) {{
            window.opener.postMessage({{ provider: "{provider}", success: false, error: "token_exchange_failed" }}, "*");
          }}
        </script>
        """
        return HTMLResponse(html, status_code=token_res.status_code)

    try:
        token_json = token_res.json()
    except Exception:
        return HTMLResponse(
            f"<h3>Token endpoint trả về không phải JSON:</h3><pre>{token_res.text}</pre>",
            status_code=502,
        )

    # ===== hậu xử lý theo nền tảng =====
    try:
        if provider == "facebook":
            await _handle_facebook_callback(db, cfg, token_json)
        elif provider == "tiktok":
            await _handle_tiktok_callback(db, cfg, token_json)
        elif provider == "youtube":
            await _handle_youtube_callback(db, cfg, token_json)
    except Exception as ex:
        return HTMLResponse(f"<h3>Lưu dữ liệu vào DB thất bại:</h3><pre>{ex}</pre>", status_code=500)

    # ===== trả HTML đóng popup & báo FE =====
    html = f"""
    <script>
      if (window.opener) {{
        window.opener.postMessage({{ provider: "{provider}", success: true }}, "*");
      }}
      window.close();
    </script>
    <p>Authentication successful! You can close this window.</p>
    """
    return HTMLResponse(html)


async def _handle_facebook_callback(db: Session, cfg: Dict, short_lived_token_json: Dict):
    import httpx
    from datetime import datetime, timedelta

    # 1) Đổi short-lived user token -> long-lived user token
    async with httpx.AsyncClient(timeout=30) as client:
        r_long = await client.get(
            cfg["token_url"],
            params={
                "grant_type": "fb_exchange_token",
                "client_id": cfg["client_id"],
                "client_secret": cfg["client_secret"],
                "fb_exchange_token": short_lived_token_json["access_token"],
            },
        )
        r_long.raise_for_status()
        t_long = r_long.json()
        user_token_ll = t_long["access_token"]
        expires_in = int(t_long.get("expires_in") or 0)
        user_expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None

        # 2) Lấy danh sách Pages (mỗi page có page access token riêng)
        r_pages = await client.get(
            "https://graph.facebook.com/v23.0/me/accounts",
            params={
                "access_token": user_token_ll,
                "fields": "id,name,access_token,picture{url}",
                "limit": 200,
            },
        )
        r_pages.raise_for_status()
        pages = (r_pages.json() or {}).get("data", [])

        saved_fb = 0
        saved_ig = 0

        for p in pages:
            page_id = p["id"]
            page_name = p.get("name") or "Facebook Page"
            page_token = p.get("access_token")
            avatar = (((p.get("picture") or {}).get("data")) or {}).get("url")

            if not page_token:
                # không có page token -> bỏ qua page này
                continue

            # 2a) Upsert Facebook channel (TOKEN = PAGE TOKEN)
            from app.repositories import channel_repo
            channel_repo.upsert(
                db, "facebook", page_id,
                defaults={
                    "name": page_name,
                    "username": page_name,
                    "avatar_url": avatar,
                    "access_token": page_token,
                    "channel_metadata": {
                        "source": "facebook_oauth",
                        "user_expires_at": user_expires_at.isoformat() if user_expires_at else None
                    },
                    "is_active": True,
                }
            )
            saved_fb += 1

            # 3) Tìm IG user id gắn với Page
            r_ig_link = await client.get(
                f"https://graph.facebook.com/v23.0/{page_id}",
                params={
                    "access_token": page_token,  # dùng PAGE TOKEN để đọc IG link
                    "fields": "instagram_business_account,connected_instagram_account"
                },
            )
            # Nếu page không liên kết IG, tiếp tục page khác
            if r_ig_link.status_code >= 400:
                continue
            ig_link = r_ig_link.json() or {}
            ig_obj = ig_link.get("instagram_business_account") or ig_link.get("connected_instagram_account")
            ig_id = (ig_obj or {}).get("id")
            if not ig_id:
                continue

            # 3a) Lấy username/avatar IG (nếu có quyền)
            ig_username = None
            ig_avatar = None
            r_ig_info = await client.get(
                f"https://graph.facebook.com/v23.0/{ig_id}",
                params={"access_token": page_token, "fields": "username,profile_picture_url"},
            )
            if r_ig_info.status_code < 400:
                j5 = r_ig_info.json() or {}
                ig_username = j5.get("username") or None
                ig_avatar = j5.get("profile_picture_url") or None

            # 3b) Upsert Instagram channel
            #     LƯU PAGE TOKEN vào access_token, và metadata.page_id để tra cứu nhanh
            channel_repo.upsert(
                db, "instagram", ig_id,
                defaults={
                    "name": ig_username or page_name,
                    "username": ig_username or page_name,
                    "avatar_url": ig_avatar,
                    "access_token": page_token,  # IG Graph cần PAGE TOKEN
                    "channel_metadata": {"page_id": page_id, "source": "facebook_oauth"},
                    "is_active": True,
                }
            )
            saved_ig += 1

        # 4) Commit tất cả thay đổi
        db.commit()

    # (Không cần return gì; callback bên ngoài sẽ render HTML “success”)
    print(f"[OAUTH:FACEBOOK] saved pages={saved_fb}, instagram={saved_ig}")

async def _handle_tiktok_callback(db: Session, cfg: Dict, token_json: Dict):
    access = token_json["access_token"]
    refresh = token_json.get("refresh_token")
    expires_in = int(token_json.get("expires_in") or 0)

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            "https://open.tiktokapis.com/v2/user/info/",
            headers={"Authorization": f"Bearer {access}"},
            params={"fields": "open_id,display_name,avatar_url"},
        )
        r.raise_for_status()
        me = (r.json().get("data") or {}).get("user") or {}

    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None

    channel_repo.upsert(
        db, "tiktok", me["open_id"],
        defaults={
            "name": me.get("display_name") or "TikTok",
            "username": me.get("display_name"),
            "avatar_url": me.get("avatar_url"),
            "access_token": access,
            "token_expires_at": expires_at,
            "channel_metadata": {"refresh_token": refresh, "scopes": cfg.get("scope")},
            "is_active": True,
        }
    )

async def _handle_youtube_callback(db: Session, cfg: Dict, token_json: Dict):
    access = token_json.get("access_token")
    refresh = token_json.get("refresh_token")
    expires_in = int(token_json.get("expires_in") or 0)
    
    # 1) Lấy danh sách channel của tài khoản
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(
            "https://www.googleapis.com/youtube/v3/channels",
            headers={"Authorization": f"Bearer {access}"},
            params={"part": "snippet", "mine": "true", "maxResults": 50},
            )
        r.raise_for_status()
        payload = r.json()
        items = payload.get("items", [])
        # 2) Nếu rỗng, vẫn nên báo rõ để bạn biết lý do
    if not items:
        raise RuntimeError(f"YouTube: no channels returned for this account. API payload={payload}")
    
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
    # 3) Upsert từng channel + COMMIT
    saved = 0
    for it in items:
        ch_id = it["id"]
        sn = it.get("snippet", {}) or {}
        title = sn.get("title") or "YouTube Channel"
        thumb = (sn.get("thumbnails") or {}).get("default") or {}

        # upsert theo (platform="youtube", external_id=ch_id)
        channel_repo.upsert(
            db, "youtube", ch_id,
            defaults={
                "name": title,
                "username": title,
                "avatar_url": thumb.get("url"),
                "access_token": access,
                "token_expires_at": expires_at,
                "channel_metadata": {"refresh_token": refresh, "scopes": cfg.get("scope")},
                "is_active": True,
            }
        )
        saved += 1
        db.commit()

# Thêm endpoint refresh token
@router.post("/{provider}/refresh")
async def refresh_token(provider: str, channel_id: int, db: Session = Depends(get_db)):
    """Refresh token cho channel"""
    channel = channel_repo.get_by_id(db, channel_id)
    if not channel or channel.platform != provider:
        raise HTTPException(404, "Channel not found")
    
    if provider == "youtube":
        await _refresh_youtube_token(db, channel)
    elif provider == "tiktok":
        await _refresh_tiktok_token(db, channel)
    # Facebook page tokens thường không cần refresh
    
    return {"success": True, "message": f"{provider} token refreshed"}

async def _refresh_youtube_token(db: Session, channel):
    """Refresh YouTube token using refresh_token"""
    cfg = OAUTH_CFG.get("youtube")
    if not cfg:
        raise HTTPException(500, "YouTube config missing")
    
    refresh_token = channel.channel_metadata.get("refresh_token")
    if not refresh_token:
        raise HTTPException(400, "No refresh token available")
    
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            cfg["token_url"],
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": cfg["client_id"],
                "client_secret": cfg["client_secret"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if res.status_code >= 400:
            raise HTTPException(res.status_code, f"Token refresh failed: {res.text}")
        
        token_data = res.json()
        access_token = token_data.get("access_token")
        # New refresh token is optional, use old one if not provided
        new_refresh = token_data.get("refresh_token", refresh_token)
        expires_in = int(token_data.get("expires_in", 3600))
        
        # Update channel in DB
        channel.access_token = access_token
        channel.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        channel.channel_metadata["refresh_token"] = new_refresh
        db.commit()
        
        return token_data


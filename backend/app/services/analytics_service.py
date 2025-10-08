


from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.analytics_repo import AnalyticsRepo

class AnalyticsService:
    @staticmethod
    def overview(db: Session) -> Dict[str, Any]:
        return AnalyticsRepo.counts(db)

    @staticmethod
    def platforms(db: Session) -> List[Dict[str, Any]]:
        rows = AnalyticsRepo.platforms(db)
        # Chuẩn hoá output
        return [
            {
                "platform": r.platform,
                "targets": int(r.targets),
                "views": int(r.views or 0),
                "reactions": int(r.reactions or 0),
                "comments": int(r.comments or 0),
                "shares": int(r.shares or 0),
            }
            for r in rows
        ]

    @staticmethod
    def top_posts(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        rows = AnalyticsRepo.top_posts(db, limit=limit)  # [(Post, views)]
        items: List[Dict[str, Any]] = []
        for post, views in rows:
            items.append({
                "post_id": post.id,
                "caption": post.caption or "",
                "hashtags": post.hashtags or "",
                "views": int(views or 0),
                "status": post.status,
                "default_scheduled_time": post.default_scheduled_time,
            })
        return items

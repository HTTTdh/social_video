



from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from app.models.post_models import Post, PostTarget
from app.models.channel_models import Channel
from app.models.video_models import Video

class AnalyticsRepo:
    @staticmethod
    def counts(db: Session):
        post_total = db.query(func.count(Post.id)).scalar() or 0
        post_posted = db.query(func.count(Post.id)).filter(Post.status == "posted").scalar() or 0
        post_scheduled = db.query(func.count(Post.id)).filter(Post.status == "scheduled").scalar() or 0
        post_failed = db.query(func.count(Post.id)).filter(Post.status == "failed").scalar() or 0
        channels = db.query(func.count(Channel.id)).scalar() or 0
        videos = db.query(func.count(Video.id)).scalar() or 0
        return {
            "posts": {"total": post_total, "posted": post_posted, "scheduled": post_scheduled, "failed": post_failed},
            "channels": channels,
            "videos": videos,
        }

    @staticmethod
    def top_posts(db: Session, limit: int = 10):
        views_expr = func.coalesce(
            func.sum(cast(PostTarget.engagement_data["post_video_views"].astext, Integer)), 0
        ).label("views")
        q = (
            db.query(Post, views_expr)
            .outerjoin(PostTarget, PostTarget.post_id == Post.id)
            .group_by(Post.id)
            .order_by(views_expr.desc(), Post.id.desc())
            .limit(limit)
        )
        return q.all()  # [(Post, views), ...]

    @staticmethod
    def platforms(db: Session):
        views_sum = func.coalesce(func.sum(cast(PostTarget.engagement_data["post_video_views"].astext, Integer)), 0)
        reacts_sum = func.coalesce(func.sum(cast(PostTarget.engagement_data["reactions"].astext, Integer)), 0)
        comments_sum = func.coalesce(func.sum(cast(PostTarget.engagement_data["comments"].astext, Integer)), 0)
        shares_sum = func.coalesce(func.sum(cast(PostTarget.engagement_data["shares"].astext, Integer)), 0)

        q = (
            db.query(
                Channel.platform.label("platform"),
                func.count(PostTarget.id).label("targets"),
                views_sum.label("views"),
                reacts_sum.label("reactions"),
                comments_sum.label("comments"),
                shares_sum.label("shares"),
            )
            .select_from(PostTarget)
            .join(Channel, PostTarget.channel_id == Channel.id)
            .group_by(Channel.platform)
            .order_by(func.count(PostTarget.id).desc())
        )
        return q.all()

#Thống kê & Xuất CSV

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import csv, io, datetime

from app.core.database import get_db
from app.api.deps import require_roles
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics_schemas import AnalyticsOverviewOut as OverviewOut
from app.schemas.analytics_schemas import AnalyticsPlatformsOut as PlatformStatsOut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/overview", response_model=OverviewOut)
def overview(
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"]))
):
    try:
        return AnalyticsService.get_overview(db)
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        raise HTTPException(500, "Failed to retrieve analytics data")

@router.get("/platforms", response_model=List[PlatformStatsOut])
def platforms(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    _ = Depends(require_roles(["admin","staff"]))
):
    try:
        return AnalyticsService.get_platform_stats(db, date_from, date_to)
    except Exception as e:
        logger.error(f"Failed to get platform stats: {e}")
        raise HTTPException(500, "Failed to retrieve platform statistics")

@router.get("/top-posts", dependencies=[Depends(require_roles(["admin","staff"]))])
def top_posts(limit: int = 10, db: Session = Depends(get_db)):
    return AnalyticsService.top_posts(db, limit=limit)

@router.get("/export", dependencies=[Depends(require_roles(["admin","staff"]))])
def export_csv(db: Session = Depends(get_db)):
    buf = io.StringIO()
    writer = csv.writer(buf)

    # Section 1: Overview
    writer.writerow(["# Overview", datetime.datetime.utcnow().isoformat() + "Z"])
    ov = AnalyticsService.overview(db)
    writer.writerow(["posts.total", ov["posts"]["total"]])
    writer.writerow(["posts.posted", ov["posts"]["posted"]])
    writer.writerow(["posts.scheduled", ov["posts"]["scheduled"]])
    writer.writerow(["posts.failed", ov["posts"]["failed"]])
    writer.writerow(["channels", ov["channels"]])  
    writer.writerow(["videos", ov["videos"]])
    writer.writerow([])

    # Section 2: Platforms
    writer.writerow(["# Platforms"])
    writer.writerow(["platform", "targets", "views", "reactions", "comments", "shares"])
    for r in AnalyticsService.platforms(db):
        writer.writerow([r["platform"], r["targets"], r["views"], r["reactions"], r["comments"], r["shares"]])
    writer.writerow([])

    # Section 3: Top posts
    writer.writerow(["# Top Posts"])
    writer.writerow(["post_id", "caption", "hashtags", "views", "status", "default_scheduled_time"])
    for t in AnalyticsService.top_posts(db, limit=50):
        writer.writerow([t["post_id"], t["caption"], t["hashtags"], t["views"], t["status"], t["default_scheduled_time"]])

    buf.seek(0)
    filename = f"analytics_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv", headers=headers)

# Python 3.9+ có zoneinfo
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

TZ_NAME = "Asia/Ho_Chi_Minh"
VN_TZ = ZoneInfo(TZ_NAME)
UTC = timezone.utc

def now_vn() -> datetime:
    return datetime.now(VN_TZ)                # 2025-09-29 10:00:00+07:00

def to_vn(dt: datetime) -> datetime:
    """Đưa bất kỳ datetime về VN (+07). Chấp nhận naive -> coi là UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(VN_TZ)

def to_utc(dt: datetime) -> datetime:
    """Đưa về UTC. Nếu đầu vào naive: coi là giờ VN."""
    if dt.tzinfo is None:                     # frontend gửi "2025-10-01T09:00:00" (giờ VN)
        dt = dt.replace(tzinfo=VN_TZ)
    return dt.astimezone(UTC)

def ensure_tz(dt: datetime) -> datetime:
    """Nếu thiếu tzinfo -> gán VN; nếu có -> giữ nguyên."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=VN_TZ)
    return dt

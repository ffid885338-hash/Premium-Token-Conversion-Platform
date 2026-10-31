from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from app.database import get_db
from app.models import User, ConversionLog, ApiKey, SystemConfig, ConversionStatus
from app.schemas import AdminStatsResponse, SystemConfigUpdate
from app.security import require_admin

router = APIRouter(prefix="/api/admin", tags=["Admin Portal"])

@router.get("/stats", response_model=AdminStatsResponse)
def get_dashboard_statistics(db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    total_conversions = db.query(func.count(ConversionLog.id)).scalar() or 0
    failed_conversions = db.query(func.count(ConversionLog.id)).filter(ConversionLog.status == ConversionStatus.FAILED).scalar() or 0
    
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_conversions = db.query(func.count(ConversionLog.id)).filter(ConversionLog.created_at >= today_start).scalar() or 0
    active_keys = db.query(func.count(ApiKey.id)).filter(ApiKey.is_active == True).scalar() or 0

    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_conversions=total_conversions,
        failed_conversions=failed_conversions,
        today_conversions=today_conversions,
        active_api_keys=active_keys
    )

@router.post("/settings")
def update_system_settings(cfg: SystemConfigUpdate, db: Session = Depends(get_db), current_admin: User = Depends(require_admin)):
    def set_key(k: str, v: str):
        item = db.query(SystemConfig).filter(SystemConfig.key == k).first()
        if not item:
            item = SystemConfig(key=k, value=v)
            db.add(item)
        else:
            item.value = v

    set_key("maintenance_mode", str(cfg.maintenance_mode))
    set_key("telegram_alerts_active", str(cfg.telegram_alerts_active))
    db.commit()
    return {"success": True, "message": "System parameters updated successfully"}
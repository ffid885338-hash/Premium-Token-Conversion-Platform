from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ConversionLog, ConversionStatus, SystemConfig
from app.schemas import TokenConversionRequest, TokenConversionResponse, ConversionItem
from app.services.token_service import TokenService
from app.services.telegram_service import telegram_service
from typing import List

router = APIRouter(prefix="/api/tokens", tags=["Token Operations"])

@router.post("/convert", response_model=TokenConversionResponse)
async def process_token_conversion(
    request: TokenConversionRequest,
    db: Session = Depends(get_db)
):
    # 1. Check Maintenance Mode
    maint = db.query(SystemConfig).filter(SystemConfig.key == "maintenance_mode").first()
    if maint and maint.value.lower() == "true":
        raise HTTPException(status_code=503, detail="Platform is currently under scheduled maintenance.")

    # 2. Verify Captcha Solution (Mathematical challenge)
    if not request.captcha_solution or len(request.captcha_solution.strip()) == 0:
        raise HTTPException(status_code=400, detail="Human verification solution missing.")

    # 3. Securely hash input
    token_hash = TokenService.hash_token(request.raw_token)

    try:
        # 4. Execute Service Conversion
        converted = await TokenService.convert(request.raw_token, request.conversion_type)
        token_hint = f"...{converted[-6:]}" if len(converted) >= 6 else "***"

        log_entry = ConversionLog(
            user_id=None,
            telegram_username=request.telegram_username,
            conversion_type=request.conversion_type,
            input_token_hash=token_hash,
            result_token_hint=token_hint,
            status=ConversionStatus.SUCCESS
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        # 5. Dispatch Telegram Notification asynchronously
        await telegram_service.notify_conversion(
            conversion_id=log_entry.id,
            conv_type=request.conversion_type.value,
            status="SUCCESS",
            username=request.telegram_username
        )

        return TokenConversionResponse(
            success=True,
            status=ConversionStatus.SUCCESS,
            converted_token=converted,
            conversion_id=log_entry.id,
            message="Token successfully transformed."
        )

    except Exception as err:
        log_entry = ConversionLog(
            user_id=None,
            telegram_username=request.telegram_username,
            conversion_type=request.conversion_type,
            input_token_hash=token_hash,
            result_token_hint="N/A",
            status=ConversionStatus.FAILED,
            error_message=str(err)
        )
        db.add(log_entry)
        db.commit()

        await telegram_service.notify_conversion(
            conversion_id=log_entry.id,
            conv_type=request.conversion_type.value,
            status="FAILED",
            username=request.telegram_username
        )

        raise HTTPException(status_code=400, detail=f"Conversion error: {str(err)}")

@router.get("/recent", response_model=List[ConversionItem])
def get_recent_conversions(db: Session = Depends(get_db)):
    logs = db.query(ConversionLog).order_by(ConversionLog.created_at.desc()).limit(15).all()
    return logs
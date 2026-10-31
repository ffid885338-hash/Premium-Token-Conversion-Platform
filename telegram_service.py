import httpx
from app.config import settings

class TelegramNotifier:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.admin_chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def notify_conversion(self, conversion_id: int, conv_type: str, status: str, username: str = None):
        if not self.bot_token or not self.admin_chat_id:
            return
            
        text = (
            f"⚡ *乙H OFFICIAL: New Conversion Alert*\n"
            f"🆔 *ID:* `{conversion_id}`\n"
            f"🔄 *Type:* `{conv_type}`\n"
            f"👤 *Telegram User:* @{username if username else 'N/A'}\n"
            f"📊 *Status:* {status}\n"
        )
        await self._send_message(self.admin_chat_id, text)

    async def send_user_alert(self, chat_id: str, message: str):
        if not self.bot_token:
            return
        await self._send_message(chat_id, message)

    async def _send_message(self, chat_id: str, text: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
                )
        except Exception as e:
            # Non-blocking log
            print(f"[Telegram Service Warning] Dispatch failed: {e}")

telegram_service = TelegramNotifier()
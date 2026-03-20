import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_otp_email(to_email: str, otp_code: str):
    """
    Sends an OTP email using EmailJS REST API.
    """
    if not all([settings.EMAILJS_SERVICE_ID, settings.EMAILJS_TEMPLATE_ID, settings.EMAILJS_PUBLIC_KEY]):
        logger.warning("EmailJS credentials not fully configured. Email not sent.")
        print(f"DEBUG OTP for {to_email}: {otp_code}")
        return True

    url = "https://api.emailjs.com/api/v1.0/email/send"
    
    payload = {
        "service_id": settings.EMAILJS_SERVICE_ID,
        "template_id": settings.EMAILJS_TEMPLATE_ID,
        "user_id": settings.EMAILJS_PUBLIC_KEY,
        "template_params": {
            "to_email": to_email,
            "email": to_email,
            "otp_code": otp_code
        }
    }
    
    # If private key is provided, use it for higher security (if required by service)
    if settings.EMAILJS_PRIVATE_KEY:
        payload["accessToken"] = settings.EMAILJS_PRIVATE_KEY

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Error sending email via EmailJS: {e}")
        return False

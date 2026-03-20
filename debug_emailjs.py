import httpx
import asyncio
from app.core.config import settings

async def test_emailjs():
    url = "https://api.emailjs.com/api/v1.0/email/send"
    payload = {
        "service_id": settings.EMAILJS_SERVICE_ID,
        "template_id": settings.EMAILJS_TEMPLATE_ID,
        "user_id": settings.EMAILJS_PUBLIC_KEY,
        "template_params": {
            "to_email": "donador@yopmail.com",
            "email": "donador@yopmail.com",
            "otp_code": "123456"
        }
    }
    if settings.EMAILJS_PRIVATE_KEY:
        payload["accessToken"] = settings.EMAILJS_PRIVATE_KEY

    print(f"Sending to {url}...")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_emailjs())

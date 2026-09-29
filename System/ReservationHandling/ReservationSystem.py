import httpx
import os
from dotenv import load_dotenv
load_dotenv()

class ReservationSystem:
    async def requestReservartion(data : dict):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(f"{os.getenv("REQUESTS")}/account/login",
                    headers={
                        "Access": 
                            f"{os.getenv("ACCESS")}"
                })
        except httpx.ConnectError as e:
            raise e
        except Exception:
            raise e
import re
import asyncio
from ErrorTypes.DetailErrors import WrongData
from System.ReservationHandling.ReservationSystem import ReservationSystem
import httpx
class ReservationHandler:
    def ValidateReservation(payload):
        pattern = r"^(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)-(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)$"
        if not re.fullmatch(pattern, payload["time"]):
            raise WrongData()
        
    def RequestReservation(payload : dict, error):
        async def _requestReservation():
            try:
                await ReservationSystem.requestReservartion(payload)
            except httpx.ConnectError:
                return error.setText("Internet Connection Error...")
            except Exception as e:
                return error.setText("err")
        asyncio.create_task(_requestReservation())
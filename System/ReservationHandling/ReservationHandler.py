import re
import asyncio
from ErrorTypes.DetailErrors import WrongData
from System.ReservationHandling.ReservationSystem import ReservationSystem
import httpx
from httpx import HTTPError
class ReservationHandler:
    def ValidateReservation(payload):
        pattern = r"^(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)-(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)$"
        if not re.fullmatch(pattern, payload["time"]):
            raise WrongData(detail="Time format is wrong, follow : 00:00AM-01:00AM")
        
        date_format = r"^\d{2}/\d{2}/\d{4}$"

        if not re.fullmatch(date_format, payload["date"]):
            raise WrongData(detail="Date format is wrong, follow : MM-DD-YYYY")
        
    def RequestReservation(button, payload : dict, error):
        async def _requestReservation():
            button.setEnabled(False)
            try:
                await ReservationSystem.requestReservartion(payload, error)
            except httpx.ConnectError:
                return error.setText("Error: Please check your internet connection.")
            except HTTPError as e:
                return error.setText("Error : " + e.response.json().get("detail"))
            except Exception as e:
                raise error.setText("Error : An Unknown Error Occured")
            finally:
                button.setEnabled(True)
        asyncio.create_task(_requestReservation())

    def GetReservation(payload : dict, reservation):
        async def _getReservation():
            try:
                data = await ReservationSystem.getReservation(payload)
                reservation.updateReservedList(data)
                return data
            except HTTPError as e:
                raise e
            except Exception as e:
                e.detail = "unknown error..."
                raise e

        asyncio.create_task(_getReservation())
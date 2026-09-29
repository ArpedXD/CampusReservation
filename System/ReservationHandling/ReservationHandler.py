import re
import asyncio
from ErrorTypes.DetailErrors import WrongData

class ReservationHandler:
    def ValidateReservation(payload):
        pattern = r"^(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)-(0[1-9]|1[0-2]):[0-5][0-9](AM|PM)$"
        if not re.fullmatch(pattern, payload["time"]):
            raise WrongData()
        
    def RequestReservation(payload):
        
        val = asyncio.create_task()
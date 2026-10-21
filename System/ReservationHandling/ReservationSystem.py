import httpx

import keyring
from QtMain.Component.dependencies.DateSorter import sort_key
import System.config
class ReservationSystem:
    async def requestReservartion(data : dict, error):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                print(data)
                response = await client.post(f"{System.config.REQUESTS}/reservation/save",
                    headers={
                        "Access": 
                            f"{System.config.ACCESS}",
                        "cookie":
                            keyring.get_password("credentials", "value")
                        },
                    json=data
                    )

                response.raise_for_status()
                if response.is_success:
                    error.setText("")
                    return
        except httpx.ConnectError as e:
            raise e
        except Exception as e:
            raise e

    async def getReservation(payload: dict):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(f"{System.config.REQUESTS}/reservation/fetchreserved",
                    headers={
                        "Access": 
                            f"{System.config.ACCESS}",
                        "cookie":
                            keyring.get_password("credentials", "value")
                        },
                    json=payload
                )

                response.raise_for_status()

                if response.is_success:
                    value = response.json()
                    return [{"name": x[2], "time": f"{x[3]}    {x[0]} - {x[1]}", "verified": x[4]}for x in value]
        except httpx.ConnectError as e:
            raise e
        except Exception as e:
            raise e
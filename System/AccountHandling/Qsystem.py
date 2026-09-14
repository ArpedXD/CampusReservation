import httpx
from dotenv import load_dotenv
import os
load_dotenv()
import keyring
from PySide6.QtWidgets import QApplication

class RequestingClasses:
    def __init__(self):
        self.link = os.getenv("REQUESTS")
        self.ACCESS = os.getenv("ACCESS")
        self.cookie = keyring.get_password("credentials", "value")

    async def loginRequest(self, username, password):
        datas = {"username": username, "password": password}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(f"{self.link}/account/login",
                    headers={
                        "Access": 
                            f"{self.ACCESS}"
                    }, json=datas)

                response.raise_for_status()

                if response.is_success:
                    value = response.json()
                    print("YAY")
                    keyring.set_password("credentials", "value", value["cookie"])
        except httpx.HTTPStatusError as e:
            raise e
        except Exception as e:
            print(str(e))
    async def signupRequest(self, mail, password):
        datas = {"username": mail, "password": password}

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(f"{self.link}/account/signup",
                    headers={
                        "Access": f"{self.ACCESS}"
                    }, json=datas)

                response.raise_for_status()

                if response.is_success:
                    value = response.json()
                    keyring.set_password("credentials", "value", value["cookie"])
                    print(keyring.get_password("credentials", "value"))
        except httpx.HTTPStatusError as e:
            raise e

    async def isLoggedIn(self):
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(f"{self.link}/account/isLoggedin", headers={
                    "Access": 
                        f"{self.ACCESS}",
                    "cookie":
                        self.cookie
                })

                response.raise_for_status()

                if response.is_success:
                    value = response.json()
                    return value
        except Exception as e:
            print(str(e))

    async def getCredentials(self):
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(f"{self.link}/account/credentials", headers={
                    "Access": 
                        f"{self.ACCESS}",
                    "cookie":
                        self.cookie
                })

                response.raise_for_status()

                if response.is_success:
                    res = response.json()
        except Exception as e:
            raise e

    async def VerifyUser(self, Credentials : dict):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(f"{self.link}/account/verify", headers={
                    "Access": 
                        f"{self.ACCESS}",
                    "cookie":
                        self.cookie
                }, json=Credentials)

                response.raise_for_status()
        except Exception as e:
            raise e
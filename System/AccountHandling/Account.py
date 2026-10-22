import asyncio
import httpx
from System.AccountHandling.Qsystem import RequestingClasses
from PySide6.QtWidgets import QApplication
from ErrorTypes.DetailErrors import BlankInputsError
import keyring
import re

class AccountHandler:
    def __init__(self):
        self.reqClass = RequestingClasses()

    def handleLogin(self, username, password, submit, errorLabel):
        async def _do_login():
            submit.setEnabled(False)
            submit.setText("Logging in...")
            try:
                await self.reqClass.loginRequest(username.text(), password.text())
                self.handleInformations()
            except httpx.ConnectError:
                errorLabel.setText("Connection Error: Please check your internet connection or try again later.")
                errorLabel.setVisible(True)
            except httpx.HTTPStatusError as e:
                try:
                    errorLabel.setText(e.response.json().get("detail"))
                except Exception as e:
                    errorLabel.setText("Unknown Error has occured.")
                errorLabel.setVisible(True)
            except Exception as e:
                errorLabel.setText("Something went wrong! Please try again")
                errorLabel.setVisible(True)
            finally:
                submit.setEnabled(True)
                submit.setText("Log in")

        asyncio.create_task(_do_login())

    def handleSignup(self, username, confirmpassword, password, submit, errorLabel):
        async def _do_login():
            submit.setEnabled(False)
            submit.setText("Signing in...")
            errorLabel.setVisible(False)
            try:
                await self.reqClass.signupRequest(username.text(), password.text())
                self.handleInformations()
            except httpx.ConnectError:
                errorLabel.setText("Connection Error: Please check your internet connection or try again later.")
                errorLabel.setVisible(True)
            except httpx.HTTPStatusError as e:
                    try:
                        errorLabel.setText(e.response.json().get("detail"))
                    except Exception as e:
                        errorLabel.setText("Unknown Error has occured.")
                    errorLabel.setVisible(True)
            except Exception as e:
                errorLabel.setText('unknown error...')
                errorLabel.setVisible(True)
            finally:
                submit.setEnabled(True)
                submit.setText("Sign in")

        asyncio.create_task(_do_login())
        
    def handleInformations(self):
        async def _handleInformations():
            try:
                data = await self.reqClass.isLoggedIn()

                if data is None:
                    return

                app_instance = QApplication.instance()

                window = app_instance.mainwindow
                window.mainSignal.emit("DoubleColumn")

                if window.main is not None:
                    window.main.updateVerificationOverlay(data["Verified"])
            except Exception as e:
                print(str(e))
        asyncio.create_task(_handleInformations())

    def handleVerify(self, first_name, last_name, year_level, college_course, student_id, err, verify_btn):
        Credentials = {
            "first_name" :first_name.text(), 
            "last_name": last_name.text(), 
            "year_level": year_level.text(),
            "college_course": college_course.text(), 
            "student_id": student_id.text()
        }
        if re.search(r'[^0-9]', Credentials["year_level"]):
            err.setText("Error: Year level must be a number")
            return
        
        student_id_format = r"^\d{2}-\d{4}-\d{6}$"

        if not re.match(student_id_format, Credentials["student_id"]):
            if re.search(r'[^0-9\-]', Credentials["student_id"]):
                err.setText("Error: Please follow '00-0000-0000' format!") 
                return
            err.setText("Error: Please follow '00-0000-00000' format!") 
            return
        
        async def _verify():
            try:
                verify_btn.setEnabled(False)
                for each in Credentials:
                    if each.rstrip() == "" or each == None:
                        raise BlankInputsError(detail="Blank Inputs")
                data = await self.reqClass.VerifyUser(err, Credentials)
            except (TypeError, ValueError) as e:
                err.setText('Error;' + str(e))
            except httpx.ConnectError:
                err.setText("Connection Error: Please check your internet connection or try again later.")
                err.setVisible(True)
            except httpx.HTTPStatusError as e:
                try:
                    err.setText(e.response.json().get("detail"))
                except Exception as e:
                    err.setText("Unknown Error has occured.")
                err.setVisible(True)
            except Exception as e:
                print('reachs')
                err.setText(f"Unknown error occured, please try again!")
            finally:
                verify_btn.setEnabled(True)
        asyncio.create_task(_verify())

    def handleLogout(self):
        application = QApplication.instance()
        application.mainwindow.mainSignal.emit("Form")
        keyring.delete_password("credentials", "value")
        return
    
    def handleFetchData(self):
        async def _handleData():
            try:
                data = await self.reqClass.GetInformations()
                if data is None:
                    return
                app_instance = QApplication.instance()
                
                app_instance.mainwindow.main.profile.ChangeProfileCredentials(data)
            except httpx.ConnectError:
                pass
            except Exception as e:
                print(e.response.json().get("detail"))
        asyncio.create_task(_handleData())

    def handleProfileReservation(self):
        async def _handleReservationData():
            try:
                data = await self.reqClass.GetProfileReservation()
                if data is None:
                    return
                app_instance = QApplication.instance()
                
                app_instance.mainwindow.main.profile.SetReservations(data)
            except httpx.ConnectError:
                pass
            except Exception as e:
                print(e.response.json().get("detail"))
        asyncio.create_task(_handleReservationData())

    def handleDelete(self, err):
        async def delete_data():
            try:
                data = await self.reqClass.deleteAccount()
                if data is None:
                    return
                if not data["Success"]:
                    return
                
                app_instance = QApplication.instance()

                window = app_instance.mainwindow
                window.mainSignal.emit("Form")
            except httpx.ConnectError:
                err.setText("Connectivity Error...")
            except httpx.HTTPStatusError as e:
                try:
                    err.setText(e.response.json().get("detail"))
                except Exception as e:
                    err.setText("Unknown Error has occured.")
                err.setVisible(True)
            except Exception as e:
                err.setText('Unknown Error occured. Please try again')
        asyncio.create_task(delete_data())

    def getusernames(self):
        async def getusername():
            try:
                data = await self.reqClass.GetInformations()
                if data is None:
                    return
                app_instance = QApplication.instance()

                app_instance.mainwindow.nav_name.setText(f"{data["Last_name"]}, {data["First_name"]}")
            except httpx.ConnectError:
                pass
            except Exception as e:
                pass
        asyncio.create_task(getusername())

    def sendFeedback(self, message, error):
        async def _sendFeedback():
            try:
                data = await self.reqClass.SendFeedBack(message)
                if data is None:
                    return
            except httpx.ConnectError:
                error.setText("Please check your internet connection.")
            except httpx.HTTPStatusError as e:
                error.setText(e.response.json().get("detail"))
            except Exception as e:
                error.setText("Something went wrong!")
        asyncio.create_task(_sendFeedback())
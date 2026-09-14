import asyncio
import httpx
from System.AccountHandling.Qsystem import RequestingClasses
from PySide6.QtWidgets import QApplication
from ErrorTypes.DetailErrors import BlankInputsError
import keyring

class AccountHandler:
    def __init__(self):
        self.reqClass = RequestingClasses()

    def handleLogin(self, username, password, submit, errorLabel):
        async def _do_login():
            submit.setEnabled(False)
            submit.setText("Logging in...")
            errorLabel.setVisible(False)
            try:
                await self.reqClass.loginRequest(username.text(), password.text())
                self.handleInformations()
            except httpx.ConnectError:
                errorLabel.setText("Connection Error: Please check your internet connection or try again later.")
                errorLabel.setVisible(True)
            except Exception as e:
                print(str(e))
                errorLabel.setText(e.response.json().get("detail"))
                errorLabel.setVisible(True)
            finally:
                submit.setEnabled(True)
                submit.setText("Log in")

        self.login_task = asyncio.create_task(_do_login())

    def handleSignup(self, username, confirmpassword, password, submit, errorLabel):
        async def _do_login():
            submit.setEnabled(False)
            submit.setText("Signing in...")
            errorLabel.setVisible(False)
            try:
                await self.reqClass.signupRequest(username.text(), password.text())
                await self.handleInformations()
            except httpx.ConnectError:
                errorLabel.setText("Connection Error: Please check your internet connection or try again later.")
                errorLabel.setVisible(True)
            except Exception as e:
                errorLabel.setText(e.response.json().get("detail"))
                errorLabel.setVisible(True)
            finally:
                submit.setEnabled(True)
                submit.setText("Sign in")

        self.signup_task = asyncio.create_task(_do_login())
        
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
        self.verify_task = asyncio.create_task(_handleInformations())

    def handleVerify(self, first_name, last_name, year_level, college_course, student_id, err):
        Credentials = {
            "first_name" :first_name.text(), 
            "last_name": last_name.text(), 
            "year_level": year_level.text(),
            "college_course": college_course.text(), 
            "student_id": student_id.text()
        }
        async def _verify():
            try:
                for each in Credentials:
                    if each.rstrip() == "" or each == None:
                        raise BlankInputsError(detail="Blank Inputs")

                data = await self.reqClass.VerifyUser(Credentials)
            except Exception as e:
                err.setText(f"An Error has Occured : {e.detail}")

        self.verify_account_task = asyncio.create_task(_verify())

    def handleLogout(self):
        application = QApplication.instance()
        application.mainwindow.mainSignal.emit("Form")
        keyring.delete_password("credentials", "value")
        return
    
    def handleFetchData(self):
        async def _handleData():
            try:
                data = await self.RequestingClasses().getCredentials()
            except httpx.ConnectError:
                pass
            except Exception as e:
                print(e.response.json().get("detail"))
        self.fetch_data = asyncio.create_task(_handleData())
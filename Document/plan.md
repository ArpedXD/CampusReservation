# Modules/Libraries to Be used

**Frontend**
- Pyside6 - UI / Websockets
- Requests - Requesting API from the backend
- Secrets - Generating A Key for login
- dotenv - Hiding endpoints -> .env 
- Nuitka/PyInstaller - Bundles pyside into a binary
- Keyring - Hides credentials in the Operating system's native credential manager 

**Backend**
- Redis - Caching
- MySQL - Hiding Informations
- dotenv - Hiding Backend credentials
- FastAPI - Handling Backend Requests


# Credentials Storing
USE **Keyring** to save sessions 
Create a class;
class SessionManager:
    def __init__(self):
        self.token = None
        self.username = None
        self.logged_in = False

    def login(self, username, token):
        self.username = username
        self.token = token
        self.logged_in = True

    def logout(self):
        self.token = None
        self.username = None
        self.logged_in = False

-- Two Choices --

Attaching to QApplication/Prop Drilling
1. app = QApplication(sys.argv)
app.session = SessionManager()

Then access it anywhere through:

self.session = QApplication.instance().session

2. Create A SessionManager() in the MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session = SessionManager()  

Then passing it through different Classes
panel = Panel(self.session) 

# Backend Security
Two Backend:
- Client
- Admin

-- Client HTTPs can only fetch data's, delete their own data, and other stuffs.
-- Admin HTTPs can EDIT, REMOVE, ADD BULK, etc in the backend.

STRICTLY TWO DIFFERENT HTTPs ENDPOINTS. MUST NOT LEAK ADMIN HTTTPs

STORE CLIENT HTTP **IN** .env file. NOT A TXT FILE OR WHAT.

Security through obscurity is not security
import os

class Config:
    SECRET_KEY = '444f220181a12acbd8461f8314364b48adb996ba07c052f3'
    MONGO_URI = 'mongodb://127.0.0.1:27017/Guichet'
    
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')

import os

class Config:
    SECRET_KEY = '444f220181a12acbd8461f8314364b48adb996ba07c052f3'
    MONGO_URI = mongodb+srv://manohitiana:hcedEcbvUBDBzusO@cluster0.f6gtwfk.mongodb.net/Gest_guichet?retryWrites=true&w=majority&appName=mongosh
    
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')

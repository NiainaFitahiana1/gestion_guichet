from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

class User(UserMixin):
    def __init__(self, nom, telephone, password, adresse, role, date_naissance, photo=None, user_id=None):
        self.id = str(user_id) if user_id else None
        self.nom = nom
        self.telephone = telephone
        self.password = password  # haché
        self.adresse = adresse
        self.role = role
        self.date_naissance = date_naissance
        self.photo = photo

    def to_dict(self):
        data = {
            "nom": self.nom,
            "telephone": self.telephone,
            "password": self.password,
            "adresse": self.adresse,
            "role": self.role,
            "date_naissance": self.date_naissance,
            "photo": self.photo
        }
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @staticmethod
    def from_dict(data):
        return User(
            data.get("nom"),
            data.get("telephone"),
            data.get("password"),
            data.get("adresse"),
            data.get("role"),
            data.get("date_naissance"),
            data.get("photo"),
            str(data.get("_id")) if data.get("_id") else None
        )

    @staticmethod
    def from_mongo(doc):
        if not doc:
            return None
        return User(
            doc["nom"],
            doc["telephone"],
            doc["password"],
            doc["adresse"],
            doc["role"],
            doc["date_naissance"],
            doc.get("photo"),
            str(doc["_id"]) if "_id" in doc else None
        )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Flask-Login Required Methods
    @property
    def is_active(self):
        return True  # Vous pouvez modifier cette logique si vous voulez une gestion d'activation d'utilisateur

    @property
    def is_authenticated(self):
        return True  # À ajuster en fonction de la logique d'authentification (si vous avez un état non authentifié)

    @property
    def is_anonymous(self):
        return False  # À ajuster en fonction de la logique d'anonymat (si nécessaire)

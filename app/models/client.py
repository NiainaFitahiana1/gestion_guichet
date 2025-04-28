from bson import ObjectId

class Client:
    def __init__(self, nom, cin, sexe, tel_perso, client_id=None):
        self.id = str(client_id) if client_id else None
        self.nom = nom
        self.cin = cin
        self.sexe = sexe
        self.tel_perso = tel_perso

    def to_dict(self):
        data = {
            "nom": self.nom,
            "cin": self.cin,
            "sexe": self.sexe,
            "tel_perso": self.tel_perso
        }
        if self.id:  # On ajoute _id uniquement s'il n'est pas None
            data["_id"] = ObjectId(self.id)
        return data

    @staticmethod
    def from_dict(data):
        return Client(
            data.get("nom"),
            data.get("cin"),
            data.get("sexe"),
            data.get("tel_perso"),
            str(data.get("_id")) if data.get("_id") else None  # Convertir en str si _id existe
        )

    @staticmethod
    def from_mongo(doc):
        if not doc:
            return None
        return Client(
            doc["nom"],
            doc["cin"],
            doc["sexe"],
            doc["tel_perso"],
            str(doc["_id"]) if "_id" in doc else None
        )

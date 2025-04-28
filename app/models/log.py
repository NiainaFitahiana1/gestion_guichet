from bson import ObjectId

class Log:
    def __init__(self, date, compte, compte2, lieu, debut_connexion, fin_connexion, log_id=None):
        self.id = str(log_id) if log_id else None
        self.date = date
        self.compte = compte
        self.compte2 = compte2
        self.lieu = lieu
        self.debut_connexion = debut_connexion
        self.fin_connexion = fin_connexion

    def to_dict(self):
        data = {
            "date": self.date,
            "compte": self.compte,
            "compte2": self.compte2,
            "lieu": self.lieu,
            "debut_connexion": self.debut_connexion,
            "fin_connexion": self.fin_connexion
        }
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @staticmethod
    def from_dict(data):
        return Log(
            data.get("date"),
            data.get("compte"),
            data.get("compte2"),
            data.get("lieu"),
            data.get("debut_connexion"),
            data.get("fin_connexion"),
            str(data.get("_id")) if data.get("_id") else None
        )

    @staticmethod
    def from_mongo(doc):
        if not doc:
            return None
        return Log(
            doc["date"],
            doc["compte"],
            doc["compte2"],
            doc["lieu"],
            doc["debut_connexion"],
            doc["fin_connexion"],
            str(doc["_id"]) if "_id" in doc else None
        )

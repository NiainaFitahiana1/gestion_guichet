from bson import ObjectId

class Desti:
    def __init__(self, destination, frais, route, responsable, desti_id=None):
        self.id = str(desti_id) if desti_id else None
        self.destination = destination
        self.frais = frais
        self.route = route
        self.responsable = responsable

    def to_dict(self):
        data = {
            "destination": self.destination,
            "frais": self.frais,
            "route": self.route,
            "responsable": self.responsable
        }
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @staticmethod
    def from_dict(data):
        return Desti(
            data.get("destination"),
            data.get("frais"),
            data.get("route"),
            data.get("responsable"),
            str(data.get("_id")) if data.get("_id") else None
        )

    @staticmethod
    def from_mongo(doc):
        if not doc:
            return None
        return Desti(
            doc["destination"],
            doc["frais"],
            doc["route"],
            doc["responsable"],
            str(doc["_id"]) if "_id" in doc else None
        )

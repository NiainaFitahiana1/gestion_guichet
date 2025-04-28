from bson import ObjectId

class Voiture:
    def __init__(self, immatriculation, cooperative, zone, adresse, proprietaire, telephone_proprietaire, nb_place, voiture_id=None):
        self.id = str(voiture_id) if voiture_id else None
        self.immatriculation = immatriculation
        self.cooperative = cooperative
        self.zone = zone
        self.adresse = adresse
        self.proprietaire = proprietaire
        self.telephone_proprietaire = telephone_proprietaire
        self.nb_place = nb_place

    def to_dict(self):
        data = {
            "immatriculation": self.immatriculation,
            "cooperative": self.cooperative,
            "zone": self.zone,
            "adresse": self.adresse,
            "proprietaire": self.proprietaire,
            "telephone_proprietaire": self.telephone_proprietaire,
            "nb_place": self.nb_place
        }
        if self.id:
            data["_id"] = ObjectId(self.id)
        return data

    @staticmethod
    def from_dict(data):
        return Voiture(
            data.get("immatriculation"),
            data.get("cooperative"),
            data.get("zone"),
            data.get("adresse"),
            data.get("proprietaire"),
            data.get("telephone_proprietaire"),
            data.get("nb_place"),
            str(data.get("_id")) if data.get("_id") else None
        )

    @staticmethod
    def from_mongo(doc):
        if not doc:
            return None
        return Voiture(
            doc["immatriculation"],
            doc["cooperative"],
            doc["zone"],
            doc["adresse"],
            doc["proprietaire"],
            doc["telephone_proprietaire"],
            doc.get("nb_place"),
            str(doc["_id"]) if "_id" in doc else None
        )

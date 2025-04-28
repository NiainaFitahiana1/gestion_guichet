from bson import ObjectId

class Voyageur:
    def __init__(self, nom, cin, sexe, tel_famille, tel_perso, adresse_depart, destination, temperature, status, voyage_id, voyageur_id=None):
        self.id = str(voyageur_id) if voyageur_id else None
        self.nom = nom
        self.cin = cin
        self.sexe = sexe
        self.tel_famille = tel_famille
        self.tel_perso = tel_perso
        self.adresse_depart = adresse_depart
        self.destination = destination
        self.temperature = temperature
        self.status = status
        self.voyage_id = str(voyage_id) if voyage_id else None  # Ajout de l'ID du voyage

    def to_dict(self):
        data = {
            "nom": self.nom,
            "cin": self.cin,
            "sexe": self.sexe,
            "tel_famille": self.tel_famille,
            "tel_perso": self.tel_perso,
            "adresse_depart": self.adresse_depart,
            "destination": self.destination,
            "temperature": self.temperature,
            "status": self.status,
            "voyage_id": ObjectId(self.voyage_id) if self.voyage_id else None  # Stocké comme ObjectId dans MongoDB
        }
        if self.id:  # On ajoute `_id` uniquement s'il n'est pas None
            data["_id"] = ObjectId(self.id)
        return data

    @staticmethod
    def from_dict(data):
        return Voyageur(
            data.get("nom"),
            data.get("cin"),
            data.get("sexe"),
            data.get("tel_famille"),
            data.get("tel_perso"),
            data.get("adresse_depart"),
            data.get("destination"),
            data.get("temperature"),
            data.get("status"),
            str(data.get("voyage_id")) if data.get("voyage_id") else None,  # Conversion en str pour éviter les erreurs
            str(data.get("_id")) if data.get("_id") else None
        )

    @staticmethod
    def from_mongo(doc):
        if not doc:
            return None
        return Voyageur(
            doc["nom"],
            doc["cin"],
            doc["sexe"],
            doc["tel_famille"],
            doc["tel_perso"],
            doc["adresse_depart"],
            doc["destination"],
            doc["temperature"],
            doc["status"],
            str(doc["voyage_id"]) if "voyage_id" in doc else None,  # Ajout du voyage_id
            str(doc["_id"]) if "_id" in doc else None
        )

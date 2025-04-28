from bson import ObjectId

class Voyage:
    def __init__(self, lieu_depart, destination, cooperative, chauffeur,total, numero_automobile, guichetier, frais, date_depart, date_arrivee, statut_voyage=None, nombre_voyageurs=None, voyage_id=None):
        self.id = str(voyage_id) if voyage_id else None
        self.lieu_depart = lieu_depart
        self.destination = destination
        self.cooperative = cooperative
        self.chauffeur = chauffeur
        self.total = total
        self.numero_automobile = numero_automobile
        self.guichetier = guichetier
        self.frais = frais
        self.date_depart = date_depart
        self.date_arrivee = date_arrivee
        self.statut_voyage = statut_voyage  # Peut être 'En cours', 'Terminé', 'Annulé', etc.
        self.nombre_voyageurs = nombre_voyageurs  # Nouveau champ

    def to_dict(self):
        data = {
            "lieu_depart": self.lieu_depart,
            "destination": self.destination,
            "cooperative": self.cooperative,
            "chauffeur": self.chauffeur,
            "total": self.total,
            "numero_automobile": self.numero_automobile,
            "guichetier": self.guichetier,
            "frais": self.frais,
            "date_depart": self.date_depart,
            "date_arrivee": self.date_arrivee,
            "statut_voyage": self.statut_voyage,
            "nombre_voyageurs": self.nombre_voyageurs  # Ajout de la colonne nombre_voyageurs
        }
        if self.id:  # On ajoute _id uniquement s'il n'est pas None
            data["_id"] = ObjectId(self.id)
        return data

    @staticmethod
    def from_dict(data):
        return Voyage(
            data.get("lieu_depart"),
            data.get("destination"),
            data.get("cooperative"),
            data.get("chauffeur"),
            data.get("total"),
            data.get("numero_automobile"),
            data.get("guichetier"),
            data.get("frais"),
            data.get("date_depart"),
            data.get("date_arrivee"),
            data.get("statut_voyage"),
            data.get("nombre_voyageurs"),
            str(data.get("_id")) if data.get("_id") else None  # Convertir en str si _id existe
        )

    @staticmethod
    def from_mongo(doc):
        if not doc:
            return None
        return Voyage(
            doc["lieu_depart"],
            doc["destination"],
            doc["cooperative"],
            doc["chauffeur"],
            doc["total"],
            doc["numero_automobile"],
            doc["guichetier"],
            doc["frais"],
            doc["date_depart"],
            doc["date_arrivee"],
            doc.get("statut_voyage"),
            doc.get("nombre_voyageurs"),
            str(doc["_id"]) if "_id" in doc else None
        )

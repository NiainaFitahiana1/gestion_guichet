from flask import Blueprint, render_template, flash
from .. import mongo
from ..models.voyage import Voyage
from datetime import datetime

public_bp = Blueprint('public_bp', __name__)

@public_bp.route("/voyages", methods=["GET"])
def voyages_aujourdhui():
    try:
        today_str = datetime.today().strftime("%Y-%m-%d")

        # On suppose que la date_depart est enregistrée au format ISO dans la base
        voyages_cursor = mongo.db.voyages.find({
            "date_depart": {"$regex": f"^{today_str}"},"statut_voyage":"encours",
        }).sort("date_depart", -1)

        voyages = [Voyage.from_mongo(doc) for doc in voyages_cursor]

        return render_template("publique/voyages_aujourdhui.html", voyages=voyages)

    except Exception as e:
        flash(f"Erreur lors du chargement des voyages : {str(e)}", "danger")
        return render_template("publique/voyages_aujourdhui.html", voyages=[])

@public_bp.route("/vitrine")
def client():
    return render_template("publique/home.html")
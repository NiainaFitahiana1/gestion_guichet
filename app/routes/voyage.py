from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required,current_user
from collections import defaultdict
from datetime import datetime
from bson import ObjectId
from .. import mongo
from ..models.voyageur import Voyageur
from ..models.voyage import Voyage
from ..middleware.decorators import role_required

voyage_bp = Blueprint('voyage_bp', __name__)

      
# 🟢 Ajouter un voyage via formulaire (GET et POST)
@voyage_bp.route("/add", methods=["GET", "POST"])
@login_required
@role_required("guichetier")
def create_voyage():
    if request.method == "POST":
        try:
            voyage = Voyage(
                lieu_depart=request.form.get("lieu_depart", "none") or "none",
                destination=request.form.get("destination", "none") or "none",
                cooperative=request.form.get("cooperative", "none") or "none",
                chauffeur=request.form.get("chauffeur", "none") or "none",
                total=request.form.get("total", "none") or "none",
                numero_automobile=request.form.get("numero_automobile", "none") or "none",
                guichetier=request.form.get("guichetier", "none") or "none",
                frais=float(request.form.get("frais", 0) or 0),
                date_depart=request.form.get("date_depart", "none") or "none",
                date_arrivee=request.form.get("date_arrivee", "none") or "none",
                statut_voyage=request.form.get("statut_voyage", "encours") or "encours",
                nombre_voyageurs=int(request.form.get("nombre_voyageurs", 0) or 0)
            )

            voyage_dict = voyage.to_dict()

            # Supprimer _id s'il est None pour éviter une erreur MongoDB
            voyage_dict.pop("_id", None)

            mongo.db.voyages.insert_one(voyage_dict)
            flash("Voyage ajouté avec succès", "success")
            return redirect(url_for("voyage_bp.list_voyages"))
        except Exception as e:
            flash(f"Erreur lors de l'ajout du voyage: {str(e)}", "danger")
    
    return render_template("add_voyage.html")  # Page d'ajout via formulaire

# 🟢 Modifier un voyage (GET et POST)
@voyage_bp.route("/edit/<id>", methods=["GET", "POST"])
@login_required
@role_required("guichetier")
def edit_voyage(id):
    try:
        voyage_doc = mongo.db.voyages.find_one({"_id": ObjectId(id)})
        if not voyage_doc:
            flash("Voyage introuvable", "warning")
            return redirect(url_for("voyage_bp.list_voyages"))
    except Exception:
        flash("ID invalide", "danger")
        return redirect(url_for("voyage_bp.list_voyages"))

    voyage = Voyage.from_mongo(voyage_doc)

    if request.method == "POST":
        try:
            updated_data = {
                "lieu_depart": request.form.get("lieu_depart"),
                "destination": request.form.get("destination"),#ceci
                "cooperative": request.form.get("cooperative"),#ceci
                "chauffeur": request.form.get("chauffeur"),#ceci
                "total": request.form.get("total"),#ceci
                "numero_automobile": request.form.get("numero_automobile"),#ceci
                "guichetier": request.form.get("guichetier"),#ceci
                "frais": float(request.form.get("frais")),#ceci
                "date_depart": request.form.get("date_depart"),#ceci
                "date_arrivee": request.form.get("date_arrivee"),
                "statut_voyage": request.form.get("statut_voyage"),
                "nombre_voyageurs": int(request.form.get("nombre_voyageurs"))
            }
            
            mongo.db.voyages.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
            flash("Voyage mis à jour avec succès", "success")
            return redirect(url_for("voyage_bp.dynamic_add"))
        except Exception as e:
            flash(f"Erreur lors de la mise à jour : {str(e)}", "danger")

    return render_template("edit_voyage.html", voyage=voyage)

@voyage_bp.route("/change-status/<id>", methods=["POST"])
@login_required
@role_required("guichetier")
def change_status(id):
    try:
        voyage_doc = mongo.db.voyages.find_one({"_id": ObjectId(id)})
        if not voyage_doc:
            flash("Voyage introuvable", "warning")
            return redirect(url_for("voyage_bp.dynamic_add"))
    except Exception:
        flash("ID invalide", "danger")
        return redirect(url_for("voyage_bp.dynamic_add"))

    if request.method == "POST":
        try:
            nouveau_statut = request.form.get("statut_voyage")
            if not nouveau_statut:
                flash("Le statut ne peut pas être vide", "warning")
                return redirect(url_for("voyage_bp.dynamic_add"))

            mongo.db.voyages.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"statut_voyage": nouveau_statut}}
            )
            flash("Statut du voyage mis à jour avec succès", "success")
        except Exception as e:
            flash(f"Erreur lors de la mise à jour du statut : {str(e)}", "danger")

    return redirect(url_for("voyage_bp.dynamic_add"))

@voyage_bp.route("/delete/<id>", methods=["POST"])
@login_required
@role_required("guichetier")
def delete_voyage(id):
    try:
        voyage_doc = mongo.db.voyages.find_one({"_id": ObjectId(id)})
        if not voyage_doc:
            flash("Voyage introuvable", "warning")
            return redirect(url_for("voyage_bp.dynamic_add"))
        
        mongo.db.voyages.delete_one({"_id": ObjectId(id)})
        flash("Voyage supprimé avec succès", "success")
    except Exception:
        flash("ID invalide ou erreur de suppression", "danger")
    
    return redirect(url_for("voyage_bp.dynamic_add"))

# 🟢 Afficher la liste des voyageurs pour un voyage spécifique
@voyage_bp.route("/<voyage_id>/voyageurs", methods=["GET"])
@login_required
@role_required("guichetier")
def list_voyageurs_for_voyage(voyage_id):
    try:
        # Chercher le voyage par ID
        voyage = mongo.db.voyages.find_one({"_id": ObjectId(voyage_id)})
        if not voyage:
            flash("Voyage introuvable", "warning")
            return redirect(url_for("voyage_bp.list_voyages"))
        
        # Récupérer la liste des voyageurs associés à ce voyage
        voyageurs = [Voyageur.from_mongo(doc) for doc in mongo.db.voyageurs.find({"voyage_id": voyage_id})]
        
        # Passer les informations à la vue
        return render_template("voyageurs_for_voyage.html", voyageurs=voyageurs, voyage=Voyage.from_mongo(voyage))
    except Exception as e:
        flash(f"Erreur lors du chargement des voyageurs : {str(e)}", "danger")
        return render_template("voyageurs_for_voyage.html", voyageurs=[], voyage_id=voyage_id)


@voyage_bp.route("/autocomplete_immatriculation", methods=["GET"])
@login_required
@role_required("guichetier")
def autocomplete_immatriculation():
    query = request.args.get("q", "")
    results = mongo.db.voitures.find({"immatriculation": {"$regex": query, "$options": "i"}}).limit(10)
    suggestions = [v["immatriculation"] for v in results]
    return jsonify(suggestions)


@voyage_bp.route("/", methods=["GET"])
def dynamic_add():
    destis = mongo.db.destis.find({})
    voitures = mongo.db.voitures.find({})
    chauffeurs = mongo.db.users.find({"role": "chauffeur"})

    # Obtenir la date d'aujourd'hui en format string 'YYYY-MM-DD'
    today_str = datetime.today().strftime("%Y-%m-%d")

    # Filtrer les voyages avec une date_depart correspondant à aujourd’hui
    voyages = mongo.db.voyages.find({
        "date_depart": today_str,
        "statut_voyage":"mameno",
    }).sort("date_depart", -1)

    return render_template(
        "voyage/add.html",
        destis=destis,
        voitures=voitures,
        chauffeurs=chauffeurs,
        voyages=voyages,
        nommer=current_user,
    )


@voyage_bp.route("/dynamic-create", methods=["POST"])
@login_required
def dynamic_create():
    try:
        # Récupération des données du formulaire
        destination = request.form.get("destination")
        numero_automobile = request.form.get("numero_automobile")
        chauffeur = request.form.get("chauffeur")
        guichetier = current_user.nom
        date_depart = request.form.get("date")
        lieu_depart = request.form.get("lieu_depart")
        
        # Récupération de la date actuelle pour date_arrivee fictive pour l’instant
        date_arrivee = None
        
        # Détermination du lieu_depart et de la coopérative à partir de la voiture
        voiture = mongo.db.voitures.find_one({"immatriculation": numero_automobile})
        if not voiture:
            flash("Voiture introuvable", "danger")
            return redirect(url_for("voyage_bp.dynamic_add"))

        cooperative = voiture.get("cooperative")
        total = voiture.get("nb_place")
        statut_voyage = "mameno"
        nombre_voyageurs = 0

        # Déterminer les frais selon la destination
        desti = mongo.db.destis.find_one({"destination": destination})
        frais = desti.get("frais") if desti else 0

        # Création du modèle Voyage
        voyage = Voyage(
            lieu_depart=lieu_depart,
            destination=destination,
            cooperative=cooperative,
            chauffeur=chauffeur,
            total=total,
            numero_automobile=numero_automobile,
            guichetier=guichetier,
            frais=frais,
            date_depart=date_depart,
            date_arrivee=date_arrivee,
            statut_voyage=statut_voyage,
            nombre_voyageurs=nombre_voyageurs
        )

        # Insertion dans MongoDB
        mongo.db.voyages.insert_one(voyage.to_dict())
        flash("Voyage créé avec succès", "success")
        return redirect(url_for("voyage_bp.dynamic_add"))
    
    except Exception as e:
        print(f"Erreur lors de la création du voyage: {e}")
        flash("Une erreur est survenue lors de la création du voyage", "danger")
        return redirect(url_for("voyage_bp.dynamic_add"))
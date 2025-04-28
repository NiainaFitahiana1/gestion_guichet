from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user,login_required
import os
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from datetime import datetime
from ..models.voiture import Voiture
from ..models.user import User
from ..models.desti import Desti
from .. import mongo

import random
home_bp = Blueprint('home_bp', __name__)

@home_bp.route("/admin")
def admin():
    nb_clients = mongo.db.clients.count_documents({})
    nb_users = mongo.db.users.count_documents({})
    destis = mongo.db.destis.find()  
    nb_voyages= mongo.db.voyages.count_documents({"statut_voyage": "termine"})
    total_voyageurs= mongo.db.voyageurs.count_documents({})

    # Chart
    voyages = mongo.db.voyages.find({"statut_voyage": "termine"}) 
    voyages_par_jour = {}
    # Récupérer toutes les destinations uniques
    destinations = set()

    for voyage in voyages:
        date_depart = datetime.strptime(voyage["date_depart"], "%Y-%m-%d").date()
        destination = voyage["destination"]
        
        # Ajouter la destination à l'ensemble
        destinations.add(destination)
        
        if date_depart not in voyages_par_jour:
            voyages_par_jour[date_depart] = {}
        
        if destination not in voyages_par_jour[date_depart]:
            voyages_par_jour[date_depart][destination] = 0
        
        voyages_par_jour[date_depart][destination] += 1
    
    labels = sorted(voyages_par_jour.keys())

    labels_str = [date.strftime('%Y-%m-%d') for date in labels]


    data = {
        label.strftime('%Y-%m-%d'): {
            dest: voyages_par_jour[label].get(dest, 0)
            for dest in destinations
        }
        for label in labels
    }

    def generate_color():
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return {
            "background": f"rgba({r}, {g}, {b}, 0.2)",
            "border": f"rgba({r}, {g}, {b}, 1)"
        }

    couleurs_par_destination = {dest: generate_color() for dest in destinations}

    datasets = []
    for destination in destinations:
        couleur = couleurs_par_destination[destination]
        datasets.append({
            "label": destination,
            "data": [data[date.strftime('%Y-%m-%d')].get(destination, 0) for date in labels],
            "backgroundColor": couleur["background"],
            "borderColor": couleur["border"],
            "borderWidth": 1
        })
    
    return render_template("admin/index.html", 
                           labels=labels_str, 
                           datasets=datasets, 
                           nb_clients=nb_clients, 
                           nb_users=nb_users,
                           destis=destis,
                           nb_voyages=nb_voyages,
                           total_voyageurs=total_voyageurs,

                           
                           )

@home_bp.route("/users")
def users():

    nb_guichetiers = mongo.db.users.count_documents({"role":"guichetier"})
    nb_chauffeurs = mongo.db.users.count_documents({"role":"chauffeur"})
    nb_voitures = mongo.db.voitures.count_documents({})
    voitures= mongo.db.voitures.find({})

    guichetiers= mongo.db.users.find({})

    return render_template("admin/gestion_users.html", 
                           nb_guichetiers=nb_guichetiers,
                           nb_chauffeurs=nb_chauffeurs,
                           nb_voitures = nb_voitures,
                           guichetiers=guichetiers,
                           user=current_user,
                           voitures = voitures,


                           )

@home_bp.route("/ajouter-guichetier", methods=["POST"])
def ajouter_guichetier():
    nom = request.form['nom']
    role = request.form['role'].lower()
    telephone = request.form['telephone']
    adresse = request.form['adresse']
    date_naissance = request.form['date_naissance']
    password = request.form['password']

    # Vérifier que le rôle est valide
    if role not in ["guichetier", "chauffeur"]:
        flash("Rôle invalide. Veuillez choisir entre 'guichetier' ou 'chauffeur'.", "danger")
        return redirect(url_for('home_bp.users'))

    # Vérification de l'unicité du nom
    existing_user = mongo.db.users.find_one({"nom": nom})
    if existing_user:
        flash(f"Un utilisateur avec le nom '{nom}' existe déjà.", "danger")
        return redirect(url_for('home_bp.users'))

    nouvel_user = User(
        nom=nom,
        telephone=telephone,
        password="",  # sera haché ensuite
        adresse=adresse,
        role=role,
        date_naissance=date_naissance
    )
    nouvel_user.set_password(password)

    mongo.db.users.insert_one(nouvel_user.to_dict())

    flash("Guichetier ajouté avec succès", "success")
    return redirect(url_for('home_bp.users'))

@home_bp.route("/edit-guichetiers/<id>", methods=["POST"])
def modifier_guichetier(id):
    mongo.db.users.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "nom": request.form['nom'],
                "telephone": request.form['telephone'],
                "adresse": request.form['adresse'],
                "date_naissance": request.form['date_naissance']
            }
        }
    )
    flash("Mis à jour avec succès", "success")
    return redirect(url_for('home_bp.users'))

@home_bp.route("/delete-guichetier/<id>", methods=["POST"])
def supprimer_guichetier(id):
    mongo.db.users.delete_one({"_id": ObjectId(id)})
    flash("Personnel supprimé avec succès", "success")
    return redirect(url_for('home_bp.users'))



@home_bp.route("/ajouter-voiture", methods=["POST"])
def ajouter_voiture():
    immatriculation = request.form['immatriculation']
    cooperative = request.form['cooperative']
    zone = request.form['zone']
    adresse = request.form['adresse']
    proprietaire = request.form['proprietaire']
    telephone_proprietaire = request.form['telephone_proprietaire']
    nb_place = request.form['nb_place']

    existante = mongo.db.voitures.find_one({"immatriculation": immatriculation})
    if existante:
        flash(f"La voiture {immatriculation} est déjà enregistrée.", "danger")
        return redirect(url_for('home_bp.users'))

    nouvelle_voiture = Voiture(
        immatriculation=immatriculation,
        cooperative=cooperative,
        zone=zone,
        adresse=adresse,
        proprietaire=proprietaire,
        telephone_proprietaire=telephone_proprietaire,
        nb_place=nb_place
    )

    mongo.db.voitures.insert_one(nouvelle_voiture.to_dict())

    flash("Voiture enregistrée avec succès", "success")
    return redirect(url_for('home_bp.users'))

@home_bp.route("/modifier-voiture/<id>", methods=["POST"])
def modifier_voiture(id):
    voiture = mongo.db.voitures.find_one({"_id": ObjectId(id)})
    if not voiture:
        flash("Voiture introuvable.", "danger")
        return redirect(url_for("home_bp.users"))

    mongo.db.voitures.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "immatriculation": request.form['immatriculation'],
            "cooperative": request.form['cooperative'],
            "zone": request.form['zone'],
            "adresse": request.form['adresse'],
            "proprietaire": request.form['proprietaire'],
            "telephone_proprietaire": request.form['telephone_proprietaire'],
            "nb_place": request.form['nb_place']
        }}
    )

    flash("Voiture modifiée avec succès", "success")
    return redirect(url_for("home_bp.users"))

@home_bp.route("/supprimer-voiture/<id>")
def supprimer_voiture(id):
    voiture = mongo.db.voitures.find_one({"_id": ObjectId(id)})
    if not voiture:
        flash("Voiture introuvable.", "danger")
    else:
        mongo.db.voitures.delete_one({"_id": ObjectId(id)})
        flash("Voiture supprimée avec succès", "success")
    return redirect(url_for("home_bp.users"))

@home_bp.route("/gestion-tarifs")
def gestion_tarifs():

    destis = list(mongo.db.destis.find())

    return render_template("admin/tarifs.html", 
                           destis=destis, 
                           user=current_user,

                           )

@home_bp.route("/ajouter-desti", methods=["POST"])
def ajouter_desti():
    destination = request.form.get("destination")
    frais = request.form.get("frais")
    route = request.form.get("route")
    responsable = request.form.get("responsable")

    if destination and frais and route and responsable:
        nouvelle_desti = Desti(destination, frais, route, responsable)
        mongo.db.destis.insert_one(nouvelle_desti.to_dict())
        flash("Destination ajoutée avec succès", "success")
    else:
        flash("Tous les champs sont requis pour ajouter une destination", "danger")

    return redirect(url_for("home_bp.gestion_tarifs"))


@home_bp.route("/modifier-desti/<desti_id>", methods=["POST"])
def modifier_desti(desti_id):
    destination = request.form.get("destination")
    frais = request.form.get("frais")
    route = request.form.get("route")
    responsable = request.form.get("responsable")

    if destination and frais and route and responsable:
        desti_modifiee = Desti(destination, frais, route, responsable, desti_id)
        mongo.db.destis.update_one(
            {"_id": ObjectId(desti_id)},
            {"$set": desti_modifiee.to_dict()}
        )
        flash("Destination modifiée avec succès", "success")
    else:
        flash("Tous les champs sont requis pour modifier une destination", "danger")

    return redirect(url_for("home_bp.gestion_tarifs"))

@home_bp.route("/supprimer-desti/<desti_id>", methods=["POST"])
def supprimer_desti(desti_id):
    try:
        mongo.db.destis.delete_one({"_id": ObjectId(desti_id)})
        flash("Destination supprimée avec succès", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression : {str(e)}", "danger")
    
    return redirect(url_for("home_bp.gestion_tarifs"))


@home_bp.route("/param")
def param():
	logs_cursor = mongo.db.logs.find().sort("date", -1)
	logs = list(logs_cursor)

	grouped_logs = {}
	for log in logs:
		date = log.get("date", "Date inconnue")
		if date not in grouped_logs:
			grouped_logs[date] = []
		grouped_logs[date].append(log)

	return render_template("admin/param.html",
		user=current_user,
		grouped_logs=grouped_logs)



@home_bp.route("/edit-superadmin", methods=["POST"])
@login_required
def edit_admin():
    user = current_user

    # Récupération des données du formulaire
    nom = request.form.get("nom")
    telephone = request.form.get("telephone")
    adresse = request.form.get("adresse")
    date_naissance = request.form.get("date_naissance")
    password = request.form.get("password")
    photo = request.files.get("photo")

    # Mise à jour des champs
    user.nom = nom
    user.telephone = telephone
    user.adresse = adresse
    user.date_naissance = date_naissance

    # Si un nouveau mot de passe est fourni
    if password:
        user.set_password(password)

    # Si une nouvelle photo est uploadée
    if photo and photo.filename != "":
        filename = secure_filename(photo.filename)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        photo.save(upload_path)
        user.photo = filename

    # Mise à jour dans la base de données MongoDB
    mongo.db.users.update_one({"_id": ObjectId(user.id)}, {"$set": user.to_dict()})

    flash("Profil mis à jour avec succès", "success")
    return redirect(url_for("home_bp.param"))
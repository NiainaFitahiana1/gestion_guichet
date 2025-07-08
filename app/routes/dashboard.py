from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from collections import defaultdict
from datetime import datetime 
from flask_login import login_required, current_user
from ..models.user import User
from ..models.client import Client
from ..models.voyageur import Voyageur
from ..models.voyage import Voyage
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from .. import mongo

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/")
@login_required
def index():
    try:
        if current_user.role == "superadmin":
            users_count = mongo.db.users.count_documents({"role": {"$ne": "superadmin"}})
            chauffeur_count = mongo.db.users.count_documents({"role": "chauffeur"})
            guichetier_count = mongo.db.users.count_documents({"role": "guichetier"})
            client_count = mongo.db.clients.count_documents({})

            # Récupération des voyages (avec date_depart correcte)
            voyages_docs = mongo.db.voyages.find({"date_depart": {"$type": "date"}})
            voyages = [Voyage.from_mongo(doc) for doc in voyages_docs]

            # Grouper par date
            voyages_by_date = defaultdict(int)
            for voyage in voyages:
                date_str = voyage.date_depart.strftime("%Y-%m-%d")
                voyages_by_date[date_str] += 1

            # Organiser pour le chart
            sorted_dates = sorted(voyages_by_date.keys())
            chart_data = {
                "labels": sorted_dates,
                "datasets": [
                    {
                        "label": "Nombre de voyages",
                        "data": [voyages_by_date[date] for date in sorted_dates],
                        "backgroundColor": "rgba(75, 192, 192, 0.4)",
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "borderWidth": 2,
                        "fill": True,
                        "tension": 0.3
                    }
                ]
            }

            return render_template(
                "dashboard/index.html",
                users_count=users_count,
                chauffeur_count=chauffeur_count,
                guichetier_count=guichetier_count,
                client_count=client_count,
                chart_data=chart_data
            )
        else:
            flash("Accès non autorisé", "danger")
            return redirect(url_for("auth_bp.login"))
    except Exception as e:
        flash(f"Erreur lors du chargement du dashboard : {str(e)}", "danger")
        return redirect(url_for("auth_bp.login"))
    
    
@dashboard_bp.route("/profile")    
@login_required
def profile():
    try:
        return render_template("dashboard/profile.html", user=current_user)
    except Exception as e:
        flash(f"Erreur lors du chargement du profil : {str(e)}", "danger")
        return redirect(url_for("auth_bp.login"))

@dashboard_bp.route("/clients")
@login_required
def list_clients():
    try:
        page = int(request.args.get("page", 1))
        per_page = 10
        search_query = request.args.get("q", "").strip()

        query_filter = {}

        # Si une recherche est faite
        if search_query:
            query_filter = {
                "$or": [
                    {"nom": {"$regex": search_query, "$options": "i"}},
                    {"cin": {"$regex": search_query, "$options": "i"}},
                    {"tel_perso": {"$regex": search_query, "$options": "i"}},
                    {"sexe": {"$regex": search_query, "$options": "i"}}
                ]
            }

        total_clients = mongo.db.clients.count_documents(query_filter)
        total_pages = (total_clients + per_page - 1) // per_page

        client_docs = (
            mongo.db.clients.find(query_filter)
            .skip((page - 1) * per_page)
            .limit(per_page)
        )

        clients = [Client.from_mongo(doc) for doc in client_docs]

        return render_template(
            "client/list.html",
            clients=clients,
            page=page,
            total_pages=total_pages,
            search_query=search_query
        )
    except Exception as e:
        flash(f"Erreur lors du chargement des clients : {str(e)}", "danger")
        return redirect(url_for("dashboard.index"))

@dashboard_bp.route("/client/<cin>/activites")
@login_required
def activites_client(cin):
    try:
        # 1. Récupérer le client à partir du CIN
        client_doc = mongo.db.clients.find_one({"cin": cin})
        if not client_doc:
            flash("Client introuvable.", "warning")
            return redirect(url_for("dashboard_bp.list_clients"))

        # 2. Récupérer les voyageurs liés par le même CIN
        voyageur_docs = mongo.db.voyageurs.find({"cin": cin})
        voyageurs = [Voyageur.from_mongo(doc) for doc in voyageur_docs]

        # 3. Extraire tous les voyage_ids
        voyage_ids = list({ObjectId(v.voyage_id) for v in voyageurs if v.voyage_id})

        # 4. Récupérer les voyages
        voyage_docs = mongo.db.voyages.find({"_id": {"$in": voyage_ids}})
        voyages = [Voyage.from_mongo(doc) for doc in voyage_docs]

        return render_template("client/activites_client.html", client=client_doc, voyageurs=voyageurs, voyages=voyages)
    
    except Exception as e:
        flash(f"Erreur lors du chargement des activités du client : {str(e)}", "danger")
        return redirect(url_for("dashboard_bp.list_clients"))

@dashboard_bp.route("/update_user", methods=["POST"])
@login_required
def update_user():
    try:
        # Récupération des champs du formulaire
        nom = request.form.get("nom")
        telephone = request.form.get("telephone")
        adresse = request.form.get("adresse")
        date_naissance = request.form.get("date_naissance")

        # Mise à jour dans la base
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {
                "nom": nom,
                "telephone": telephone,
                "adresse": adresse,
                "date_naissance": date_naissance
            }}
        )

        # Mettre à jour current_user (en mémoire)
        current_user.nom = nom
        current_user.telephone = telephone
        current_user.adresse = adresse
        current_user.date_naissance = date_naissance

        flash("Profil mis à jour avec succès.", "success")
        return redirect(url_for("dashboard.profile"))

    except Exception as e:
        flash(f"Erreur lors de la mise à jour du profil : {str(e)}", "danger")
        return redirect(url_for("dashboard.profile"))

@dashboard_bp.route("/change_password", methods=["POST"])
@login_required
def change_password():
    try:
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        # Vérifie l'ancien mot de passe
        if not current_user.check_password(current_password):
            flash("Mot de passe actuel incorrect.", "danger")
            return redirect(url_for("dashboard_bp.profile"))

        if new_password != confirm_password:
            flash("Le nouveau mot de passe et la confirmation ne correspondent pas.", "warning")
            return redirect(url_for("dashboard_bp.profile"))

        # Hache le nouveau mot de passe
        hashed_password = generate_password_hash(new_password)

        # Met à jour dans MongoDB
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {"password": hashed_password}}
        )

        flash("Mot de passe mis à jour avec succès.", "success")
        return redirect(url_for("dashboard_bp.profile"))

    except Exception as e:
        flash(f"Erreur lors du changement de mot de passe : {str(e)}", "danger")
        return redirect(url_for("dashboard_bp.profile"))

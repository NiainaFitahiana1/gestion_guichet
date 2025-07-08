from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from bson import ObjectId
from .. import mongo
from ..models.user import User
from ..middleware.decorators import role_required

from datetime import datetime


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		try:
			nom = request.form["nom"]
			password = request.form["password"]

			user_data = mongo.db.users.find_one({"nom": nom})

			if user_data and check_password_hash(user_data["password"], password):
				user = User.from_mongo(user_data)
				login_user(user)
				flash("Connexion réussie !", "success")

				# Enregistrer un log de connexion
				now = datetime.now()
				log = {
					"date": now.strftime("%Y-%m-%d"),
					"compte": user_data.get("role", "Inconnu"),  # rôle ici
					"compte2": nom,  # nom de l'utilisateur
					"lieu": request.remote_addr,
					"debut_connexion": now.strftime("%H:%M:%S"),
					"fin_connexion": None
				}
				mongo.db.logs.insert_one(log)

				# Redirection selon le rôle
				if user_data.get("role") == "superadmin":
					return redirect(url_for("home_bp.admin"))
				elif user_data.get("role") == "guichetier":
					return redirect(url_for("voyage_bp.dynamic_add"))

				return render_template("auth/login.html")

			else:
				flash("Nom d'utilisateur ou mot de passe incorrect", "danger")

		except Exception as e:
			flash(f"Erreur lors de la connexion : {str(e)}", "danger")

	return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
	try:
		last_log = mongo.db.logs.find_one(
			{"compte2": current_user.nom}, 
			sort=[("_id", -1)]
		)

		if last_log:
			mongo.db.logs.update_one(
				{"_id": last_log["_id"]},
				{"$set": {"fin_connexion": datetime.now().strftime("%H:%M:%S")}}
			)
	except Exception as e:
		flash(f"Erreur lors de la mise à jour du log de déconnexion : {str(e)}", "danger")

	logout_user()
	flash("Vous avez été déconnecté", "info")
	return redirect(url_for("auth_bp.login"))

@auth_bp.route("/add_user", methods=["GET", "POST"])
@login_required
@role_required("superadmin")
def add_user():
    if current_user.role != "superadmin":
        flash("Accès non autorisé", "danger")
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        try:
            nom = request.form["nom"]
            telephone = request.form["telephone"]
            password = request.form["password"]
            adresse = request.form["adresse"]
            role = request.form["role"]
            date_naissance = request.form["date_naissance"]
            photo = request.form.get("photo", None)

            new_user = User(
                nom=nom,
                telephone=telephone,
                password=password,
                adresse=adresse,
                role=role,
                date_naissance=date_naissance,
                photo=photo
            )
            new_user.set_password(password)

            mongo.db.users.insert_one(new_user.to_dict())
            flash("Utilisateur ajouté avec succès", "success")
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            flash(f"Erreur lors de l'ajout de l'utilisateur : {str(e)}", "danger")

    return render_template("users/add_user.html")


@auth_bp.route("/users", methods=["GET"])
@login_required
def list_users():
    try:
        users = [
            User.from_mongo(doc)
            for doc in mongo.db.users.find({"role": {"$ne": "superadmin"}})
        ]
        return render_template("users/list.html", users=users)
    except Exception as e:
        flash(f"Erreur lors du chargement des utilisateurs : {str(e)}", "danger")
        return render_template("users/list.html", users=[])

@auth_bp.route("/edit_user/<user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    if current_user.role != "superadmin":
        flash("Accès non autorisé", "danger")
        return redirect(url_for("dashboard.index"))

    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        flash("Utilisateur introuvable", "danger")
        return redirect(url_for("auth_bp.list_users"))

    user = User.from_mongo(user_data)

    if request.method == "POST":
        try:
            user.nom = request.form["nom"]
            user.telephone = request.form["telephone"]
            user.adresse = request.form["adresse"]
            user.role = request.form["role"]
            user.date_naissance = request.form["date_naissance"]

            mongo.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": user.to_dict()}
            )
            flash("Utilisateur modifié avec succès", "success")
            return redirect(url_for("auth_bp.list_users"))
        except Exception as e:
            flash(f"Erreur lors de la modification : {str(e)}", "danger")

    return render_template("users/edit_user.html", user=user)


@auth_bp.route("/delete_user/<user_id>", methods=["GET"])
@login_required
def delete_user(user_id):
    if current_user.role != "superadmin":
        flash("Accès non autorisé", "danger")
        return redirect(url_for("dashboard.index"))

    try:
        mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        flash("Utilisateur supprimé avec succès", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression : {str(e)}", "danger")

    return redirect(url_for("auth_bp.list_users"))

from flask import Blueprint, request, render_template, redirect, url_for, flash, Response
from flask_login import login_required
from weasyprint import HTML
from bson import ObjectId
from datetime import datetime
from .. import mongo
from ..models.voyageur import Voyageur
from ..models.client import Client
from ..middleware.decorators import role_required
voyageur_bp = Blueprint('voyageur_bp', __name__)

@voyageur_bp.route("/list/<voyage_id>", methods=["GET"])
@login_required
@role_required("guichetier")
def list_voyageurs(voyage_id):
    try:
        # Récupérer le voyage correspondant à l'ID
        voyage = mongo.db.voyages.find_one({"_id": ObjectId(voyage_id)})
        if not voyage:
            flash("Voyage non trouvé.", "warning")
            return redirect(url_for("voyage_bp.view_voyage", id=voyage_id))

        # Récupérer tous les voyageurs associés à ce voyage
        voyageurs = mongo.db.voyageurs.find({"voyage_id": ObjectId(voyage_id)})
        nombre_voyageurs = mongo.db.voyageurs.count_documents({"voyage_id": ObjectId(voyage_id)})

        # Passer les données du voyage aussi au template
        return render_template("voyageurs.html", voyageurs=voyageurs, voyage=voyage, voyage_id=voyage_id, nombre_voyageurs=nombre_voyageurs)
    except Exception as e:
        flash(f"Erreur lors de la récupération des voyageurs: {str(e)}", "danger")
        return redirect(url_for("voyage_bp.view_voyage", id=voyage_id))

# 🟢 Ajouter un voyageur à un voyage spécifique (POST)
@voyageur_bp.route("/add/<voyage_id>", methods=["GET", "POST"])
@login_required
@role_required("guichetier")
def create_voyageur(voyage_id):
    if request.method == "POST":
        try:
            # Récupérer les données du formulaire
            nom = request.form.get("nom", "none")
            cin = request.form.get("cin", "none")
            sexe = request.form.get("sexe", "none")
            tel_famille = request.form.get("tel_famille", "none")
            tel_perso = request.form.get("tel_perso", "none")
            adresse_depart = request.form.get("adresse_depart", "none")
            destination = request.form.get("destination", "none")
            temperature = float(request.form.get("temperature", 0))
            status = request.form.get("status", "none")

            # Vérifier si le client existe
            existing_client = mongo.db.clients.find_one({"cin": cin})
            if not existing_client:
                new_client = Client(nom, cin, sexe, tel_perso)
                mongo.db.clients.insert_one(new_client.to_dict())

            # Créer le voyageur
            voyageur = Voyageur(
                nom=nom,
                cin=cin,
                sexe=sexe,
                tel_famille=tel_famille,
                tel_perso=tel_perso,
                adresse_depart=adresse_depart,
                destination=destination,
                temperature=temperature,
                status=status,
                voyage_id=voyage_id
            )

            voyageur_dict = voyageur.to_dict()
            voyageur_dict.pop("_id", None)

            # Insérer le voyageur
            mongo.db.voyageurs.insert_one(voyageur_dict)

            # 🔁 Incrémenter nombre_voyageurs dans le document voyage
            mongo.db.voyages.update_one(
                {"_id": ObjectId(voyage_id)},
                {"$inc": {"nombre_voyageurs": 1}}  # Incrément de +1
            )

            flash("Voyageur ajouté avec succès", "success")
            return redirect(url_for("voyageur_bp.list_voyageurs", voyage_id=voyage_id))
        except Exception as e:
            flash(f"Erreur lors de l'ajout du voyageur: {str(e)}", "danger")

    return render_template("voyageurs.html", voyage_id=voyage_id)

@voyageur_bp.route("/edit/<voyage_id>/<voyageur_id>", methods=["GET", "POST"])
@login_required
@role_required("guichetier")
def edit_voyageur(voyage_id, voyageur_id):
    try:
        voyageur = mongo.db.voyageurs.find_one({"_id": ObjectId(voyageur_id)})
        
        if request.method == "POST":
            # Mettre à jour les informations du voyageur
            mongo.db.voyageurs.update_one(
                {"_id": ObjectId(voyageur_id)},
                {
                    "$set": {
                        "nom": request.form.get("nom"),
                        "cin": request.form.get("cin"),
                        "sexe": request.form.get("sexe"),
                        "tel_famille": request.form.get("tel_famille"),
                        "tel_perso": request.form.get("tel_perso"),
                        "adresse_depart": request.form.get("adresse_depart"),
                        "destination": request.form.get("destination"),
                        "temperature": float(request.form.get("temperature")),
                        "status": request.form.get("status")
                    }
                }
            )
            flash("Voyageur modifié avec succès", "success")
            return redirect(url_for("voyageur_bp.list_voyageurs", voyage_id=voyage_id))  # Rediriger vers la liste des voyageurs
        else:
            return render_template("edit_voyageur.html", voyageur=voyageur, voyage_id=voyage_id)
    
    except Exception as e:
        flash(f"Erreur lors de la modification du voyageur: {str(e)}", "danger")
        return redirect(url_for("voyageur_bp.list_voyageurs", voyage_id=voyage_id))

@voyageur_bp.route("/delete/<voyage_id>/<voyageur_id>", methods=["POST"])
@login_required
@role_required("guichetier")
def delete_voyageur(voyage_id, voyageur_id):
    try:
        mongo.db.voyageurs.delete_one({"_id": ObjectId(voyageur_id)})
        flash("Voyageur supprimé avec succès", "success")

        mongo.db.voyages.update_one(
            {"_id": ObjectId(voyage_id)},
            {"$inc": {"nombre_voyageurs": -1}}  # ✅ Correction ici
        )

    except Exception as e:
        flash(f"Erreur lors de la suppression du voyageur: {str(e)}", "danger")
    
    # Rediriger vers la liste des voyageurs du voyage
    return redirect(url_for("voyageur_bp.list_voyageurs", voyage_id=voyage_id))


@voyageur_bp.route('/list/<voyage_id>/pdf', methods=['GET'])
# @login_required
# @role_required("guichetier")
# @role_required("superadmin")
def export_voyageurs_pdf(voyage_id):
    try:
        voyageurs = mongo.db.voyageurs.find({"voyage_id": ObjectId(voyage_id)})

        voyage = mongo.db.voyages.find_one({"_id": ObjectId(voyage_id)})

        chauffeur_nom = voyage.get("chauffeur")
        chauffeur_doc = mongo.db.users.find_one({"nom": chauffeur_nom})
        chauffeur_telephone = chauffeur_doc.get("telephone") if chauffeur_doc else "Inconnu"

        date_depart = voyage.get("date_depart")
        if isinstance(date_depart, str):
            try:
                date_depart = datetime.fromisoformat(date_depart)
            except ValueError:
                date_depart = None
        date_depart_fr = date_depart.strftime('%d/%m/%Y') if date_depart else "Inconnue"

        html = render_template(
            "voyageurs_pdf.html",
            voyageurs=voyageurs,
            voyage=voyage,
            chauffeur_telephone=chauffeur_telephone,
            date_depart_fr=date_depart_fr
        )
        pdf = HTML(string=html, base_url=request.base_url).write_pdf()

        return Response(pdf, mimetype='application/pdf',
                        headers={"Content-Disposition": "inline;filename=liste_voyageurs.pdf"})
    except Exception as e:
        flash(f"Erreur lors de l'exportation PDF : {str(e)}", "danger")
        return redirect(url_for("voyageur_bp.list_voyageurs", voyage_id=voyage_id))
    


@voyageur_bp.route("/listes/<voyage_id>", methods=["GET"])
@login_required
def listes_voyageurs(voyage_id):
    try:
        voyage = mongo.db.voyages.find_one({"_id": ObjectId(voyage_id)})
        if not voyage:
            flash("Voyage non trouvé.", "warning")
            return redirect(url_for("voyage_bp.view_voyage", id=voyage_id))

        voyageurs = mongo.db.voyageurs.find({"voyage_id": ObjectId(voyage_id)})
        nombre_voyageurs = mongo.db.voyageurs.count_documents({"voyage_id": ObjectId(voyage_id)})

        return render_template("voyageur/list.html", voyageurs=voyageurs, voyage=voyage, voyage_id=voyage_id, nombre_voyageurs=nombre_voyageurs)
    except Exception as e:
        flash(f"Erreur lors de la récupération des voyageurs: {str(e)}", "danger")
        return redirect(url_for("voyage_bp.view_voyage", id=voyage_id))
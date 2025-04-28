from app import mongo
from app.models.user import User

def init_db():
    try:
        # Vérifier si un utilisateur superadmin existe déjà
        superadmin_exists = mongo.db.users.find_one({"role": "superadmin"})
        
        if not superadmin_exists:
            # Créer un super administrateur
            superadmin = User(
                nom="NIAINA",  # Nom
                telephone="0000000000",  # Téléphone
                password="superadminpassword",  # Mot de passe (sera haché)
                adresse="123 Rue Admin",  # Adresse
                role="superadmin",  # Rôle
                date_naissance="1980-01-01",  # Date de naissance
                photo=None  # Photo (optionnel)
            )
            
            # Hacher le mot de passe avant de l'ajouter dans la base de données
            superadmin.set_password(superadmin.password)
            
            # Insérer le superadmin dans la base de données
            mongo.db.users.insert_one(superadmin.to_dict())
            print("Super administrateur ajouté avec succès !")
        else:
            print("Le super administrateur existe déjà.")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données : {str(e)}")

if __name__ == "__main__":
    init_db()

# Utiliser l'image Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Exposer le port Flask (par défaut 5000)
EXPOSE 5000

# Définir la variable d'environnement Flask
ENV FLASK_APP=app
ENV FLASK_ENV=development

# Commande pour lancer l'application Flask
CMD ["flask", "run", "--host=0.0.0.0"]

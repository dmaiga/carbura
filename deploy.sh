#!/bin/bash
set -e

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "🔍 Vérification des migrations manquantes..."
if ! python manage.py makemigrations --check --dry-run; then
    echo "⚠️ Génération des migrations..."
    python manage.py makemigrations --noinput
fi

echo "📦 Application des migrations..."
python manage.py migrate --noinput

echo "👤 Vérification du superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    print('Création du superuser...')
    User.objects.create_superuser(
        username='admin',
        password='changeMe'
    )
    print('✅ Superuser créé !')
else:
    print('ℹ️ Superuser existe déjà')
"

echo "📂 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "✅ Setup terminé !"

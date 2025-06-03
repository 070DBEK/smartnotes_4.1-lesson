# Virtual environment yaratish
python -m venv blog_env
source blog_env/bin/activate  # Linux/Mac
# yoki
blog_env\Scripts\activate  # Windows

# Dependencies o'rnatish
pip install -r requirements.txt

# Logs papkasini yaratish
mkdir logs

# Static va media papkalarini yaratish
mkdir static
mkdir media
mkdir media/profiles

# Migrationlar yaratish
python manage.py makemigrations users
python manage.py makemigrations posts
python manage.py makemigrations comments
python manage.py makemigrations notifications
python manage.py makemigrations search

# Migrationlarni qo'llash
python manage.py migrate

# Superuser yaratish
python manage.py createsuperuser

# Static fayllarni yig'ish
python manage.py collectstatic --noinput

# Serverni ishga tushirish
python manage.py runserver
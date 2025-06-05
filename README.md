# 🚀 Django Blog API

![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)
![DRF](https://img.shields.io/badge/DRF-3.14.0-red.svg)
![JWT](https://img.shields.io/badge/JWT-Auth-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Zamonaviy blog va forum uchun to'liq RESTful API. Django va Django REST Framework yordamida qurilgan.

## ✨ Asosiy xususiyatlar

- 🔐 **JWT Autentifikatsiya**: Xavfsiz token-based autentifikatsiya
- ✉️ **Email tasdiqlash**: Foydalanuvchilar email orqali ro'yxatdan o'tishadi
- 👤 **Foydalanuvchi profillari**: Bio va rasm yuklash imkoniyati
- 👥 **Follow/Unfollow**: Foydalanuvchilarni kuzatish tizimi
- 📝 **Postlar**: Postlarni yaratish, o'qish, yangilash va o'chirish
- 💬 **Kommentariyalar**: Postlarga izoh qoldirish
- ❤️ **Like/Unlike**: Postlar va kommentariyalarga like qo'yish
- 🔔 **Bildirishnomalar**: Foydalanuvchi harakatlari uchun bildirishnomalar
- 🔍 **Qidiruv**: Postlar, kommentariyalar va foydalanuvchilar bo'yicha qidiruv

## 🛠️ Texnologiyalar

- **Backend**: Django 4.2, Django REST Framework 3.14
- **Autentifikatsiya**: JWT (Simple JWT)
- **Ma'lumotlar bazasi**: SQLite (development), PostgreSQL (production)
- **Email**: SMTP orqali email yuborish
- **Media**: Rasmlarni saqlash va boshqarish

## 📋 O'rnatish

### 1. Loyihani yuklab olish

\`\`\`bash
git clone https://github.com/username/django-blog-api.git
cd django-blog-api
\`\`\`

### 2. Virtual muhit yaratish

\`\`\`bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
\`\`\`

### 3. Kerakli paketlarni o'rnatish

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Muhit sozlamalarini sozlash

\`\`\`bash
cp .env.example .env
\`\`\`

`.env` faylini tahrirlang:

\`\`\`
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email sozlamalari (production uchun)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
\`\`\`

### 5. Ma'lumotlar bazasini yaratish

\`\`\`bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
\`\`\`

### 6. Serverni ishga tushirish

\`\`\`bash
python manage.py runserver
\`\`\`

API `http://localhost:8000/api/v1/` manzilida ishga tushadi.

## 📁 Loyiha tuzilishi

\`\`\`
config/
├── accounts/          # Foydalanuvchi autentifikatsiyasi va profillar
│   ├── models.py      # User, Profile, Follow modellari
│   ├── serializers.py # API serializerlar
│   ├── views.py       # API ko'rinishlar
│   ├── urls.py        # URL yo'naltirish
│   └── admin.py       # Admin interfeysi
├── blog/              # Blog funksionalligi
│   ├── models.py      # Post, Comment, Like, Notification modellari
│   ├── serializers.py # API serializerlar
│   ├── views.py       # API ko'rinishlar
│   ├── urls.py        # URL yo'naltirish
│   └── admin.py       # Admin interfeysi
├── config/            # Loyiha sozlamalari
│   ├── settings.py    # Django sozlamalari
│   ├── urls.py        # Asosiy URL yo'naltirish
│   └── wsgi.py        # WSGI konfiguratsiyasi
├── requirements.txt   # Python bog'liqliklar
├── manage.py          # Django boshqaruv skripti
└── README.md          # Ushbu fayl
\`\`\`

## 🔌 API Endpointlar

### Autentifikatsiya
- `POST /api/v1/auth/register/` - Yangi foydalanuvchi ro'yxatdan o'tkazish
- `POST /api/v1/auth/login/` - Tizimga kirish
- `POST /api/v1/auth/logout/` - Tizimdan chiqish
- `POST /api/v1/auth/token/refresh/` - Access tokenni yangilash
- `POST /api/v1/auth/verify-email/` - Email manzilini tasdiqlash
- `POST /api/v1/auth/password-reset/` - Parolni tiklash so'rovi
- `POST /api/v1/auth/password-reset/confirm/` - Parolni tiklashni tasdiqlash

### Foydalanuvchilar va Profillar
- `GET /api/v1/auth/users/me/` - Joriy foydalanuvchi ma'lumotlarini olish
- `GET /api/v1/auth/profiles/me/` - Joriy foydalanuvchi profilini olish
- `PUT /api/v1/auth/profiles/me/` - Joriy foydalanuvchi profilini yangilash
- `GET /api/v1/auth/profiles/{username}/` - Foydalanuvchi profilini olish
- `POST /api/v1/auth/profiles/{username}/follow/` - Foydalanuvchini kuzatish
- `POST /api/v1/auth/profiles/{username}/unfollow/` - Foydalanuvchini kuzatishni to'xtatish
- `GET /api/v1/auth/profiles/{username}/followers/` - Kuzatuvchilarni olish
- `GET /api/v1/auth/profiles/{username}/following/` - Kuzatilayotganlarni olish

### Postlar
- `GET /api/v1/posts/` - Postlar ro'yxatini olish (filtrlash, qidiruv, sahifalash)
- `POST /api/v1/posts/` - Yangi post yaratish
- `GET /api/v1/posts/{id}/` - Post tafsilotlarini olish
- `PUT /api/v1/posts/{id}/` - Postni yangilash
- `DELETE /api/v1/posts/{id}/` - Postni o'chirish (soft delete)
- `POST /api/v1/posts/{id}/like/` - Postga like qo'yish
- `POST /api/v1/posts/{id}/unlike/` - Postdan like ni olib tashlash

### Kommentariyalar
- `GET /api/v1/posts/{post_id}/comments/` - Post uchun kommentariyalar ro'yxatini olish
- `POST /api/v1/posts/{post_id}/comments/` - Kommentariya yaratish
- `GET /api/v1/comments/{id}/` - Kommentariya tafsilotlarini olish
- `PUT /api/v1/comments/{id}/` - Kommentariyani yangilash
- `DELETE /api/v1/comments/{id}/` - Kommentariyani o'chirish
- `POST /api/v1/comments/{id}/like/` - Kommentariyaga like qo'yish
- `POST /api/v1/comments/{id}/unlike/` - Kommentariyadan like ni olib tashlash

### Bildirishnomalar
- `GET /api/v1/notifications/` - Bildirishnomalar ro'yxatini olish
- `POST /api/v1/notifications/{id}/mark-as-read/` - Bildirishnomani o'qilgan deb belgilash
- `POST /api/v1/notifications/mark-all-as-read/` - Barcha bildirishnomalarni o'qilgan deb belgilash

### Qidiruv
- `GET /api/v1/search/?q={query}&type={type}` - Postlar, kommentariyalar, foydalanuvchilarni qidirish

## 🔒 Autentifikatsiya

API JWT autentifikatsiyasidan foydalanadi. Tokenni Authorization headerida qo'shing:

\`\`\`
Authorization: Bearer <your-access-token>
\`\`\`

### Login misoli

1. **Ro'yxatdan o'tish**:
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
  }'
\`\`\`

2. **Email tasdiqlash** (konsolda token tekshiring):
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/auth/verify-email/ \
  -H "Content-Type: application/json" \
  -d '{"token": "verification-token-from-email"}'
\`\`\`

3. **Login**:
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
\`\`\`

## 🧪 Testlash

### Testlarni ishga tushirish
\`\`\`bash
python manage.py test
\`\`\`

### curl bilan qo'lda testlash

Post yaratish:
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Birinchi postim",
    "content": "Bu mening birinchi postim mazmuni."
  }'
\`\`\`

## 🚀 Production ga chiqarish

### 1. Muhit o'zgaruvchilari
Production da quyidagi muhit o'zgaruvchilarini o'rnating:

\`\`\`env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
EMAIL_HOST=smtp.yourdomain.com
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-email-password
SITE_URL=https://yourdomain.com
\`\`\`

### 2. Ma'lumotlar bazasi
Production da PostgreSQL dan foydalaning:

\`\`\`bash
pip install psycopg2-binary
\`\`\`

### 3. Statik fayllar
Statik fayllarni xizmat qilish uchun WhiteNoise yoki CDN dan foydalaning:

\`\`\`bash
pip install whitenoise
\`\`\`

### 4. Xavfsizlik
- HTTPS dan foydalaning
- Xavfsiz cookie-larni sozlang
- CORS ni to'g'ri sozlang
- Sirlar uchun muhit o'zgaruvchilaridan foydalaning

## 📝 Litsenziya

Ushbu loyiha MIT litsenziyasi ostida litsenziyalangan.

## 🤝 Hissa qo'shish

1. Loyihani fork qiling
2. Feature branch yarating
3. O'zgarishlaringizni qo'shing
4. Testlar qo'shing
5. Pull request yuboring

## 📞 Yordam

Yordam uchun support@yourdomain.com ga xat yuboring yoki GitHub da muammo yarating.

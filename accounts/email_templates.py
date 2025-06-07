def get_password_reset_email(username, reset_token, site_url):
    """Password reset email template"""
    return f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parolni tiklash - Zamka</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007bff;
        }}
        .logo {{
            font-size: 32px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }}
        .title {{
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .content {{
            margin-bottom: 30px;
        }}
        .token-box {{
            background: #f8f9fa;
            border: 2px dashed #007bff;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }}
        .token {{
            font-family: 'Courier New', monospace;
            font-size: 18px;
            font-weight: bold;
            color: #007bff;
            letter-spacing: 2px;
            word-break: break-all;
        }}
        .button {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .warning {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
            color: #856404;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }}
        .social-links {{
            margin: 20px 0;
        }}
        .social-links a {{
            color: #007bff;
            text-decoration: none;
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🔐 Zamka</div>
            <h1 class="title">Parolni tiklash</h1>
        </div>

        <div class="content">
            <p>Assalomu alaykum, <strong>{username}</strong>!</p>

            <p>Siz Zamka platformasida parolni tiklash so'rovini yubordingiz. Yangi parol o'rnatish uchun quyidagi tokendan foydalaning:</p>

            <div class="token-box">
                <p><strong>Tasdiqlash tokeni:</strong></p>
                <div class="token">{reset_token}</div>
            </div>

            <p style="text-align: center;">
                <a href="{site_url}/reset-password?token={reset_token}" class="button">
                    🔑 Parolni tiklash
                </a>
            </p>

            <div class="warning">
                <strong>⚠️ Muhim eslatma:</strong>
                <ul>
                    <li>Bu token 24 soat davomida amal qiladi</li>
                    <li>Tokenni hech kimga bermang</li>
                    <li>Agar siz parolni tiklashni so'ramagan bo'lsangiz, bu xabarni e'tiborsiz qoldiring</li>
                </ul>
            </div>

            <p>Agar yuqoridagi tugma ishlamasa, quyidagi linkni brauzeringizga nusxalang:</p>
            <p style="word-break: break-all; color: #007bff;">
                {site_url}/reset-password?token={reset_token}
            </p>
        </div>

        <div class="footer">
            <p><strong>Zamka jamoasi</strong></p>
            <p>Zamonaviy blog va ijtimoiy tarmoq platformasi</p>

            <div class="social-links">
                <a href="#">📧 Yordam</a> |
                <a href="#">🌐 Veb-sayt</a> |
                <a href="#">📱 Telegram</a>
            </div>

            <p style="font-size: 12px; color: #999;">
                Bu avtomatik xabar. Iltimos, javob bermang.<br>
                © 2024 Zamka. Barcha huquqlar himoyalangan.
            </p>
        </div>
    </div>
</body>
</html>
    """


def get_verification_email(username, verification_token, site_url):
    """Email verification template"""
    return f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email tasdiqlash - Zamka</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #28a745;
        }}
        .logo {{
            font-size: 32px;
            font-weight: bold;
            color: #28a745;
            margin-bottom: 10px;
        }}
        .title {{
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }}
        .content {{
            margin-bottom: 30px;
        }}
        .token-box {{
            background: #f8f9fa;
            border: 2px dashed #28a745;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }}
        .token {{
            font-family: 'Courier New', monospace;
            font-size: 18px;
            font-weight: bold;
            color: #28a745;
            letter-spacing: 2px;
            word-break: break-all;
        }}
        .button {{
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .welcome-box {{
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }}
        .social-links {{
            margin: 20px 0;
        }}
        .social-links a {{
            color: #28a745;
            text-decoration: none;
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🎉 Zamka</div>
            <h1 class="title">Xush kelibsiz!</h1>
        </div>

        <div class="content">
            <div class="welcome-box">
                <h2>🎊 Tabriklaymiz, {username}!</h2>
                <p>Siz Zamka oilasiga qo'shildingiz!</p>
            </div>

            <p>Zamka platformasiga ro'yxatdan o'tganingiz uchun rahmat! Email manzilingizni tasdiqlash uchun quyidagi tokendan foydalaning:</p>

            <div class="token-box">
                <p><strong>Tasdiqlash tokeni:</strong></p>
                <div class="token">{verification_token}</div>
            </div>

            <p style="text-align: center;">
                <a href="{site_url}/verify-email?token={verification_token}" class="button">
                    ✅ Email ni tasdiqlash
                </a>
            </p>

            <h3>🚀 Zamka da nima qilishingiz mumkin:</h3>
            <ul>
                <li>📝 Qiziqarli postlar yozing</li>
                <li>💬 Boshqalar bilan muloqot qiling</li>
                <li>👥 Do'stlaringizni kuzating</li>
                <li>❤️ Yoqtirgan kontentlaringizga like qo'ying</li>
                <li>🔔 Yangiliklar haqida bildirishnoma oling</li>
            </ul>

            <p>Agar yuqoridagi tugma ishlamasa, quyidagi linkni brauzeringizga nusxalang:</p>
            <p style="word-break: break-all; color: #28a745;">
                {site_url}/verify-email?token={verification_token}
            </p>
        </div>

        <div class="footer">
            <p><strong>Zamka jamoasi</strong></p>
            <p>Zamonaviy blog va ijtimoiy tarmoq platformasi</p>

            <div class="social-links">
                <a href="#">📧 Yordam</a> |
                <a href="#">🌐 Veb-sayt</a> |
                <a href="#">📱 Telegram</a>
            </div>

            <p style="font-size: 12px; color: #999;">
                Bu avtomatik xabar. Iltimos, javob bermang.<br>
                © 2024 Zamka. Barcha huquqlar himoyalangan.
            </p>
        </div>
    </div>
</body>
</html>
    """


def get_welcome_email(username):
    """Welcome email after verification"""
    return f"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xush kelibsiz - Zamka</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 32px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }}
        .celebration {{
            background: linear-gradient(135deg, #007bff, #6f42c1);
            color: white;
            border-radius: 8px;
            padding: 30px;
            text-align: center;
            margin: 20px 0;
        }}
        .features {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
        }}
        .feature {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .button {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🎊 Zamka</div>
        </div>

        <div class="celebration">
            <h1>🎉 Tabriklaymiz, {username}!</h1>
            <p>Email manzilingiz muvaffaqiyatli tasdiqlandi!</p>
            <p>Endi Zamka platformasining barcha imkoniyatlaridan foydalanishingiz mumkin.</p>
        </div>

        <div class="features">
            <div class="feature">
                <h3>📝 Post yozing</h3>
                <p>O'z fikrlaringizni dunyoga ulashing</p>
            </div>
            <div class="feature">
                <h3>👥 Do'stlar toping</h3>
                <p>Qiziqarli odamlarni kuzating</p>
            </div>
            <div class="feature">
                <h3>💬 Muloqot qiling</h3>
                <p>Kommentlar orqali suhbatlashing</p>
            </div>
            <div class="feature">
                <h3>🔔 Xabardor bo'ling</h3>
                <p>Muhim yangiliklar haqida bilib oling</p>
            </div>
        </div>

        <p style="text-align: center;">
            <a href="#" class="button">🚀 Zamka ga kirish</a>
        </p>

        <div class="footer">
            <p><strong>Zamka jamoasi</strong></p>
            <p>© 2024 Zamka. Barcha huquqlar himoyalangan.</p>
        </div>
    </div>
</body>
</html>
    """

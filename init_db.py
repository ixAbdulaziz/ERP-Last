from app import create_app, db

# إنشاء نسخة من التطبيق للوصول إلى إعدادات قاعدة البيانات
app = create_app()

# استخدام سياق التطبيق لتنفيذ أوامر قاعدة البيانات
with app.app_context():
    print("--- (Re)Creating all database tables... ---")
    # هذا الأمر سيضمن وجود كل الجداول والأعمدة الصحيحة
    db.create_all()
    print("--- Database tables created successfully. ---")

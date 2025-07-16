import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename

# --- الإعداد الأولي ---
app = Flask(__name__)

# --- إعدادات أساسية ---
# هذا المفتاح السري ضروري لعمل الرسائل السريعة (flash messages)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-development')
# مسار مجلد حفظ المرفقات
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- ربط قاعدة البيانات ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- تصميم نماذج قاعدة البيانات (ترجمة الجداول إلى كود) ---
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    invoices = db.relationship('Invoice', backref='supplier', lazy=True)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(255), nullable=False)
    invoice_number = db.Column(db.String(100), nullable=False)
    invoice_type = db.Column(db.String(100), nullable=False)
    category_name = db.Column(db.String(100), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    amount_pre_tax = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    attachment_path = db.Column(db.String(255), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- مسارات التطبيق (الصفحات) ---

@app.route('/')
def home():
    # سنقوم ببرمجة لوحة المعلومات هنا لاحقاً
    return render_template('home.html')

@app.route('/add', methods=['GET', 'POST'])
def add_invoice():
    # --- منطق حفظ الفاتورة ---
    if request.method == 'POST':
        # 1. الحصول على البيانات من النموذج
        supplier_name = request.form.get('supplier_name')
        
        # 2. التحقق من المورد أو إنشاء واحد جديد
        supplier = Supplier.query.filter_by(name=supplier_name).first()
        if not supplier:
            supplier = Supplier(name=supplier_name)
            db.session.add(supplier)
            # نستخدم flush للحصول على ID للمورد الجديد قبل الحفظ النهائي
            db.session.flush()

        # 3. التعامل مع المرفقات
        attachment_filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file.filename != '':
                attachment_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename))

        # 4. تجميع بيانات الفاتورة
        invoice_date_str = request.form.get('invoice_date')
        amount = float(request.form.get('amount_pre_tax'))
        tax = float(request.form.get('tax_amount'))
        
        new_invoice = Invoice(
            supplier_id=supplier.id,
            supplier_name=supplier.name,
            invoice_number=request.form.get('invoice_number'),
            invoice_type=request.form.get('invoice_type'),
            category_name=request.form.get('category_name'),
            invoice_date=datetime.strptime(invoice_date_str, '%Y-%m-%d').date(),
            amount_pre_tax=amount,
            tax_amount=tax,
            total_amount=amount + tax,
            notes=request.form.get('notes'),
            attachment_path=attachment_filename
        )

        # 5. حفظ الفاتورة في قاعدة البيانات
        db.session.add(new_invoice)
        db.session.commit()

        flash('تم حفظ الفاتورة بنجاح!', 'success')
        return redirect(url_for('home'))

    # --- عرض صفحة الإضافة (GET Request) ---
    return render_template('add.html')

# --- واجهات برمجة التطبيقات (APIs) للميزات الذكية ---
@app.route('/api/search_suppliers')
def search_suppliers():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    # يبحث عن الموردين الذين يبدأ اسمهم بالحروف المكتوبة
    suppliers = Supplier.query.filter(Supplier.name.like(f'{query}%')).limit(5).all()
    
    # يرجع النتائج بصيغة JSON
    return jsonify([{'id': s.id, 'name': s.name} for s in suppliers])

# ... يمكنك إضافة مسارات view.html و purchase-orders.html هنا لاحقاً ...

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

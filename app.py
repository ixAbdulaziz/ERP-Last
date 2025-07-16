import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- الإعداد الأولي ---
app = Flask(__name__)

# --- ربط قاعدة البيانات ---
# قراءة رابط قاعدة البيانات الذي يوفره Railway تلقائياً
db_url = os.environ.get('DATABASE_URL')
# تعديل بسيط على الرابط ليتوافق مع SQLAlchemy
if db_url and db_url.startswith("mysql://"):
    db_url = db_url.replace('mysql://', 'mysql+mysqlclient://', 1)

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
    return render_template('home.html')

@app.route('/add', methods=['GET'])
def add_invoice_form():
    return render_template('add.html')

# --- واجهات برمجة التطبيقات (APIs) للميزات الذكية ---
# سنقوم ببرمجة المنطق الخاص بها في الخطوة التالية
@app.route('/api/search_suppliers')
def search_suppliers():
    return jsonify([]) 

# الأمر التالي ضروري ليعمل التطبيق على Railway
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

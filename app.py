import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename

db = SQLAlchemy()

# --- النماذج (Models) ---
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    invoices = db.relationship('Invoice', backref='supplier', lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='supplier', lazy=True, cascade="all, delete-orphan")
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True, cascade="all, delete-orphan")

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    invoices = db.relationship('Invoice', backref='purchase_order', lazy=True)

# --- مصنع التطبيقات ---
def create_app():
    app = Flask(__name__, static_folder='static')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key')
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("mysql://"):
        db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # --- المسارات ---
    @app.route('/')
    def home():
        suppliers_count = Supplier.query.count()
        invoices_count = Invoice.query.count()
        total_amount_query = db.session.query(db.func.sum(Invoice.total_amount)).scalar()
        total_amount = total_amount_query or 0
        purchase_orders_count = PurchaseOrder.query.count()
        latest_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
        latest_suppliers = []
        supplier_ids = set()
        for invoice in latest_invoices:
            if invoice.supplier and invoice.supplier.id not in supplier_ids:
                latest_suppliers.append(invoice.supplier)
                supplier_ids.add(invoice.supplier.id)
        return render_template('home.html', suppliers_count=suppliers_count, invoices_count=invoices_count, total_amount=total_amount, purchase_orders_count=purchase_orders_count, latest_invoices=latest_invoices, latest_suppliers=latest_suppliers)

    # --- << تم تعديل هذه الدالة لاستقبال وحفظ البيانات >> ---
    @app.route('/add', methods=['GET', 'POST'])
    def add_invoice_page():
        if request.method == 'POST':
            # 1. الحصول على البيانات من النموذج
            supplier_name = request.form.get('supplier_name')
            
            # 2. التحقق من المورد أو إنشاء واحد جديد
            supplier = Supplier.query.filter_by(name=supplier_name).first()
            if not supplier:
                supplier = Supplier(name=supplier_name)
                db.session.add(supplier)
                db.session.flush()

            # 3. التعامل مع المرفقات
            attachment_filename = None
            if 'attachment' in request.files:
                file = request.files['attachment']
                if file.filename != '':
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
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

        # عند طلب GET، اعرض الصفحة فقط
        return render_template('add.html')

    @app.route('/view')
    def view_page(): return render_template('view.html')
    
    @app.route('/purchase-orders')
    def purchase_orders_page(): return render_template('purchase-orders.html')

    @app.route('/health')
    def health_check(): return "OK", 200

    # يمكنك إضافة واجهات API هنا لاحقًا...

    return app

app = create_app()

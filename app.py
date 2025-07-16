import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename

# --- الإعداد الأولي ---
app = Flask(__name__)

# --- إعدادات أساسية ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key-for-development')
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
    # العلاقات مع الجداول الأخرى
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
    # للربط مع أوامر الشراء لاحقًا
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

# --- مسارات التطبيق (الصفحات) ---

@app.route('/')
def home():
    # حساب الإحصائيات الرئيسية
    suppliers_count = Supplier.query.count()
    invoices_count = Invoice.query.count()
    total_amount_query = db.session.query(db.func.sum(Invoice.total_amount)).scalar()
    total_amount = total_amount_query or 0
    purchase_orders_count = 0 # مؤقت

    # جلب آخر 5 فواتير
    latest_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()

    # جلب آخر الموردين بناءً على آخر الفواتير
    latest_suppliers = []
    supplier_ids = set()
    for invoice in latest_invoices:
        if invoice.supplier and invoice.supplier.id not in supplier_ids:
            latest_suppliers.append(invoice.supplier)
            supplier_ids.add(invoice.supplier.id)

    return render_template(
        'home.html', 
        suppliers_count=suppliers_count,
        invoices_count=invoices_count,
        total_amount=total_amount,
        purchase_orders_count=purchase_orders_count,
        latest_invoices=latest_invoices,
        latest_suppliers=latest_suppliers
    )


@app.route('/add', methods=['GET', 'POST'])
def add_invoice():
    if request.method == 'POST':
        supplier_name = request.form.get('supplier_name')
        
        supplier = Supplier.query.filter_by(name=supplier_name).first()
        if not supplier:
            supplier = Supplier(name=supplier_name)
            db.session.add(supplier)
            db.session.flush()

        attachment_filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file.filename != '':
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                attachment_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename))

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

        db.session.add(new_invoice)
        db.session.commit()

        flash('تم حفظ الفاتورة بنجاح!', 'success')
        return redirect(url_for('home'))

    return render_template('add.html')

# --- << إضافة المسارات الجديدة هنا >> ---

@app.route('/view')
def view_suppliers():
    # استعلام لجلب جميع الموردين مع حساب إحصائياتهم
    suppliers_with_stats = db.session.query(
        Supplier,
        db.func.count(Invoice.id).label('invoice_count'),
        db.func.sum(Invoice.total_amount).label('total_invoiced')
    ).outerjoin(Invoice, Supplier.id == Invoice.supplier_id)\
     .group_by(Supplier.id, Supplier.name)\
     .order_by(Supplier.name)\
     .all()

    return render_template('view.html', suppliers_with_stats=suppliers_with_stats)

@app.route('/supplier/<int:supplier_id>')
def supplier_details(supplier_id):
    # جلب المورد المحدد أو إظهار خطأ 404
    supplier = Supplier.query.get_or_404(supplier_id)
    
    # جلب فواتير هذا المورد مرتبة بالأحدث
    invoices = Invoice.query.filter_by(supplier_id=supplier_id).order_by(Invoice.invoice_date.desc()).all()
    
    # جلب مدفوعات هذا المورد مرتبة بالأحدث
    payments = Payment.query.filter_by(supplier_id=supplier_id).order_by(Payment.payment_date.desc()).all()
    
    # حساب الإحصائيات المالية
    total_invoiced = sum(inv.total_amount for inv in invoices)
    total_paid = sum(pay.amount for pay in payments)
    outstanding_balance = total_invoiced - total_paid
    
    return render_template(
        'supplier_details.html',
        supplier=supplier,
        invoices=invoices,
        payments=payments,
        total_invoiced=total_invoiced,
        total_paid=total_paid,
        outstanding_balance=outstanding_balance
    )


@app.route('/api/search_suppliers')
def search_suppliers():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    suppliers = Supplier.query.filter(Supplier.name.like(f'{query}%')).limit(5).all()
    
    return jsonify([{'id': s.id, 'name': s.name} for s in suppliers])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

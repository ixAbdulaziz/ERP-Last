import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename

db = SQLAlchemy()

# --- النماذج (Models) كما هي ---
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    invoices = db.relationship('Invoice', backref='supplier', lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='supplier', lazy=True, cascade="all, delete-orphan")

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    invoice_number = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    attachment_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)

# --- مصنع التطبيقات ---
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key')
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("mysql://"):
        db_url = db_url.replace('mysql://', 'mysql+pymysql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # --- مسارات عرض الصفحات ---
    @app.route('/')
    def home(): return render_template('home.html')

    @app.route('/add')
    def add_invoice_page(): return render_template('add.html')

    @app.route('/view')
    def view_page(): return render_template('view.html')

    # --- واجهة برمجة التطبيقات (API) ---
    @app.route('/api/data', methods=['GET'])
    def get_all_data():
        suppliers = Supplier.query.all()
        invoices = Invoice.query.all()
        payments = Payment.query.all()

        return jsonify({
            'suppliers': [{'id': s.id, 'name': s.name} for s in suppliers],
            'invoices': [{'id': i.id, 'supplier_id': i.supplier_id, 'invoice_number': i.invoice_number, 'total_amount': float(i.total_amount), 'date': i.invoice_date.strftime('%Y-%m-%d'), 'notes': i.notes} for i in invoices],
            'payments': [{'id': p.id, 'supplier_id': p.supplier_id, 'amount': float(p.amount), 'date': p.payment_date.strftime('%Y-%m-%d'), 'notes': p.notes} for p in payments]
        })

    @app.route('/api/suppliers/<int:supplier_id>/edit', methods=['POST'])
    def edit_supplier(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        data = request.json
        new_name = data.get('name')
        if not new_name:
            return jsonify({'success': False, 'message': 'الاسم الجديد مطلوب'}), 400
        
        # تحديث اسم المورد في كل الفواتير المرتبطة (إذا أردت ذلك)
        # for invoice in supplier.invoices:
        #     invoice.supplier_name = new_name
            
        supplier.name = new_name
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم تحديث اسم المورد بنجاح'})

    @app.route('/api/invoices/<int:invoice_id>/delete', methods=['POST'])
    def delete_invoice(invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف الفاتورة بنجاح'})

    @app.route('/api/payments', methods=['POST'])
    def add_payment_api():
        data = request.json
        supplier_id = data.get('supplier_id')
        amount = data.get('amount')
        date_str = data.get('date')

        if not all([supplier_id, amount, date_str]):
             return jsonify({'success': False, 'message': 'بيانات ناقصة'}), 400

        new_payment = Payment(
            supplier_id=supplier_id,
            amount=float(amount),
            payment_date=datetime.strptime(date_str, '%Y-%m-%d').date(),
            notes=data.get('notes')
        )
        db.session.add(new_payment)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تمت إضافة الدفعة بنجاح', 'payment': {'id': new_payment.id, 'supplier_id': new_payment.supplier_id, 'amount': float(new_payment.amount), 'date': new_payment.payment_date.strftime('%Y-%m-%d'), 'notes': new_payment.notes}}), 201

    # أضف هنا باقي الـ APIs للحذف والتعديل مستقبلاً...

    return app

app = create_app()

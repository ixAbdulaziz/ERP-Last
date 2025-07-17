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

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    invoice_number = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    # ملاحظة: تم إزالة الأعمدة غير المستخدمة حاليًا لتبسيط الأمر
    
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text, nullable=True)

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

    # --- المسارات التي تعرض صفحات HTML ---
    @app.route('/')
    def home(): return render_template('home.html')
    @app.route('/add')
    def add_invoice_page(): return render_template('add.html')
    @app.route('/view')
    def view_page(): return render_template('view.html')
    @app.route('/health')
    def health_check(): return "OK", 200

    # --- << واجهة برمجة التطبيقات (API) >> ---
    @app.route('/api/data', methods=['GET'])
    def get_all_data():
        suppliers = Supplier.query.order_by(Supplier.name).all()
        invoices = Invoice.query.order_by(Invoice.invoice_date.desc()).all()
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
        
        return jsonify({
            'suppliers': [{'id': s.id, 'name': s.name} for s in suppliers],
            'invoices': [{'id': i.id, 'supplier_id': i.supplier_id, 'invoice_number': i.invoice_number, 'total_amount': float(i.total_amount), 'date': i.invoice_date.strftime('%Y-%m-%d'), 'notes': i.notes} for i in invoices],
            'payments': [{'id': p.id, 'supplier_id': p.supplier_id, 'amount': float(p.amount), 'date': p.payment_date.strftime('%Y-%m-%d'), 'notes': p.notes} for p in payments]
        })

    @app.route('/api/invoices', methods=['POST'])
    def add_invoice_api():
        data = request.json
        supplier_name = data.get('supplier')
        
        supplier = Supplier.query.filter_by(name=supplier_name).first()
        if not supplier:
            supplier = Supplier(name=supplier_name)
            db.session.add(supplier)
            db.session.commit()

        new_invoice = Invoice(
            supplier_id=supplier.id,
            invoice_number=data.get('invoiceNumber'),
            total_amount=float(data.get('totalAmount')),
            invoice_date=datetime.strptime(data.get('date'), '%Y-%m-%d').date(),
            notes=data.get('notes')
        )
        db.session.add(new_invoice)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تمت إضافة الفاتورة بنجاح'}), 201
    
    @app.route('/api/invoices/<int:invoice_id>/delete', methods=['POST'])
    def delete_invoice_api(invoice_id):
        invoice = Invoice.query.get_or_404(invoice_id)
        db.session.delete(invoice)
        db.session.commit()
        return jsonify({'success': True, 'message': 'تم حذف الفاتورة بنجاح'})
        
    @app.route('/api/payments', methods=['POST'])
    def add_payment_api():
        data = request.json
        payment = Payment(
            supplier_id=int(data['supplier_id']),
            amount=float(data['amount']),
            payment_date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            notes=data.get('notes')
        )
        db.session.add(payment)
        db.session.commit()
        return jsonify({
            'success': True, 
            'payment': {
                'id': payment.id, 
                'supplier_id': payment.supplier_id,
                'amount': float(payment.amount), 
                'date': payment.payment_date.strftime('%Y-%m-%d'), 
                'notes': payment.notes
            }
        }), 201

    return app

app = create_app()

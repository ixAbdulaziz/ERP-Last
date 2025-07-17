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
    # --- << التغيير هنا: قمنا بتحديد مجلد static بشكل صريح >> ---
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
    def home(): return render_template('home.html')
    @app.route('/add')
    def add_invoice_page(): return render_template('add.html')
    @app.route('/view')
    def view_page(): return render_template('view.html')
    @app.route('/purchase-orders')
    def purchase_orders_page(): return render_template('purchase-orders.html')
    @app.route('/health')
    def health_check(): return "OK", 200

    # يمكنك إضافة واجهات API هنا لاحقًا...

    return app

app = create_app()

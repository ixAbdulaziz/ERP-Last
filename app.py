from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
import os
from datetime import datetime
import json

# إنشاء تطبيق Flask
app = Flask(__name__)

# إعدادات Flask
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# إعداد MySQL مباشرة من متغيرات البيئة
app.config['MYSQL_HOST'] = os.environ.get('MYSQLHOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQLDATABASE')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQLPORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# تهيئة MySQL
mysql = MySQL(app)

# دالة لإنشاء الجداول تلقائياً
def create_tables():
    try:
        cursor = mysql.connection.cursor()
        
        # إنشاء جدول الموردين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # إنشاء جدول الفواتير
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INT AUTO_INCREMENT PRIMARY KEY,
                invoice_number VARCHAR(100) NOT NULL UNIQUE,
                supplier_id INT NOT NULL,
                invoice_date DATE NOT NULL,
                invoice_type VARCHAR(100),
                category VARCHAR(100),
                amount_before_tax DECIMAL(10, 2) NOT NULL,
                tax_amount DECIMAL(10, 2) NOT NULL,
                total_amount DECIMAL(10, 2) NOT NULL,
                notes TEXT,
                file_data LONGTEXT,
                file_type VARCHAR(50),
                file_name VARCHAR(255),
                file_size INT,
                purchase_order_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        ''')
        
        # إنشاء جدول أوامر الشراء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                po_number VARCHAR(100) NOT NULL UNIQUE,
                supplier_id INT NOT NULL,
                description TEXT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                pdf_file_data LONGTEXT,
                pdf_file_name VARCHAR(255),
                pdf_file_size INT,
                created_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        ''')
        
        # إنشاء جدول المدفوعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                supplier_id INT NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                payment_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        ''')
        
        mysql.connection.commit()
        cursor.close()
        print("تم إنشاء الجداول بنجاح!")
    except Exception as e:
        print(f"خطأ في إنشاء الجداول: {e}")

# محاولة إنشاء الجداول عند بدء التطبيق
@app.before_first_request
def initialize_database():
    create_tables()

# المسارات (Routes)

@app.route('/')
def index():
    """الصفحة الرئيسية - إعادة توجيه إلى home"""
    return redirect(url_for('home'))

@app.route('/home')
def home():
    """صفحة لوحة المعلومات"""
    return render_template('home.html')

@app.route('/add')
def add():
    """صفحة إضافة فاتورة"""
    return render_template('add.html')

@app.route('/view')
def view():
    """صفحة عرض الفواتير"""
    return render_template('view.html')

@app.route('/purchase-orders')
def purchase_orders():
    """صفحة أوامر الشراء"""
    return render_template('purchase-orders.html')

# مسار لاختبار الاتصال بقاعدة البيانات
@app.route('/test-db')
def test_db():
    """اختبار الاتصال بقاعدة البيانات"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        return jsonify({
            'status': 'success',
            'message': 'تم الاتصال بقاعدة البيانات بنجاح!',
            'database': os.environ.get('MYSQLDATABASE', 'غير محدد')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'فشل الاتصال بقاعدة البيانات: {str(e)}'
        }), 500

# مسار للتحقق من المتغيرات
@app.route('/check-env')
def check_env():
    """التحقق من متغيرات البيئة"""
    return jsonify({
        'MYSQLHOST': 'تم التعيين' if os.environ.get('MYSQLHOST') else 'مفقود',
        'MYSQLUSER': 'تم التعيين' if os.environ.get('MYSQLUSER') else 'مفقود',
        'MYSQLPASSWORD': 'تم التعيين' if os.environ.get('MYSQLPASSWORD') else 'مفقود',
        'MYSQLDATABASE': 'تم التعيين' if os.environ.get('MYSQLDATABASE') else 'مفقود',
        'MYSQLPORT': os.environ.get('MYSQLPORT', 'مفقود')
    })

# API Endpoints - سنضيفها لاحقاً

# تشغيل التطبيق
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

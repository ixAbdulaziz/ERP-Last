from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_mysqldb import MySQL
from config import Config
import json
from datetime import datetime

# إنشاء تطبيق Flask
app = Flask(__name__)
app.config.from_object(Config)

# إعداد MySQL
mysql = MySQL()

# تكوين MySQL
app.config['MYSQL_HOST'] = Config.MYSQL_HOST
app.config['MYSQL_USER'] = Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = Config.MYSQL_DB
app.config['MYSQL_PORT'] = Config.MYSQL_PORT
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# تهيئة MySQL
mysql.init_app(app)

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

# API Endpoints - سنضيفها لاحقاً

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)

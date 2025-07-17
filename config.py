import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

class Config:
    # إعدادات Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # إعدادات MySQL من Railway
    MYSQL_HOST = os.environ.get('MYSQLHOST')
    MYSQL_USER = os.environ.get('MYSQLUSER')
    MYSQL_PASSWORD = os.environ.get('MYSQLPASSWORD')
    MYSQL_DB = os.environ.get('MYSQLDATABASE')
    MYSQL_PORT = int(os.environ.get('MYSQLPORT', 3306))
    
    # إعدادات عامة
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

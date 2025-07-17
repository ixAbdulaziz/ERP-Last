import MySQLdb
from config import Config
import sys

def init_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    try:
        # الاتصال بقاعدة البيانات
        conn = MySQLdb.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            passwd=Config.MYSQL_PASSWORD,
            db=Config.MYSQL_DB,
            port=Config.MYSQL_PORT,
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # قراءة ملف SQL
        with open('database.sql', 'r', encoding='utf8') as f:
            sql_commands = f.read()
        
        # تنفيذ الأوامر
        for command in sql_commands.split(';'):
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    conn.commit()
                except MySQLdb.Error as e:
                    if 'already exists' in str(e):
                        print(f"تم تخطي: {str(e)}")
                    else:
                        print(f"خطأ: {str(e)}")
        
        print("تم إنشاء قاعدة البيانات بنجاح!")
        
        cursor.close()
        conn.close()
        
    except MySQLdb.Error as e:
        print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()

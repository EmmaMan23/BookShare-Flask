import pymysql
import os
from dotenv import load_dotenv

load_dotenv()


connection = pymysql.connect(
    user = os.environ.get("MYSQL_USER"),
    password = os.environ.get("MYSQL_PASSWORD"),
    host = os.environ.get("MYSQL_HOST"),
    port = os.environ.get("MYSQL_PORT"),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor)

database = os.environ.get('MYSQL_DB')

with connection.cursor() as cursor:
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    print(f"✅ Database '{database}' created or already exists.")
    connection.commit()
    connection.close()
import psycopg2
import os

class Database:
    def __init__(self, _=None):
        try:
            self.connection = psycopg2.connect(
                dbname=os.getenv("PGDATABASE"),
                user=os.getenv("PGUSER"),
                password=os.getenv("PGPASSWORD"),
                host=os.getenv("PGHOST"),
                port=os.getenv("PGPORT"),
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(f"[❌ ERROR db connection] {e}")
            raise

    def setup_database(self):
        try:
            self.create_table('PRODUCTS', {
                'url': 'TEXT PRIMARY KEY',
                'title': 'TEXT NOT NULL',
                'current_price': 'REAL NOT NULL',
                'last_price': 'REAL NOT NULL',
                'best_price': 'REAL NOT NULL',
                'last_revision': 'TIMESTAMP NOT NULL',
                'img': 'TEXT'
            })
        except Exception as e:
            print(f"[❌ ERROR setup_database] {e}")
            self.connection.rollback()

    def create_table(self, table_name, columns):
        try:
            columns_with_types = ', '.join(f"{col} {typ}" for col, typ in columns.items())
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})")
            self.connection.commit()
        except Exception as e:
            print(f"[❌ ERROR create_table] {e}")
            self.connection.rollback()

    def insert_product(self, product):
        try:
            self.cursor.execute("""
                INSERT INTO PRODUCTS (url, title, current_price, last_price, best_price, last_revision, img)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s)
                ON CONFLICT (url) DO NOTHING
            """, (
                product['url'], product['title'], product['current_price'],
                product['current_price'], product['current_price'], product.get('img', None)
            ))
            self.connection.commit()
        except Exception as e:
            print(f"[❌ ERROR insert_product] {e}")
            self.connection.rollback()

    def delete_product(self, url):
        try:
            self.cursor.execute("DELETE FROM PRODUCTS WHERE url = %s", (url,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"[❌ ERROR delete_product] {e}")
            self.connection.rollback()
            return False

    def update_product(self, product):
        try:
            self.cursor.execute("""
                UPDATE PRODUCTS
                SET current_price = %s, last_price = %s, best_price = %s, last_revision = NOW()
                WHERE url = %s
            """, (
                product['current_price'], product['last_price'],
                product['best_price'], product['url']
            ))
            self.connection.commit()
        except Exception as e:
            print(f"[❌ ERROR update_product] {e}")
            self.connection.rollback()

    def fetch_all_products(self):
        try:
            self.cursor.execute("SELECT * FROM PRODUCTS ORDER BY title DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"[❌ ERROR fetch_all_products] {e}")
            self.connection.rollback()
            return []

    def fetch_product(self, url):
        try:
            self.cursor.execute("SELECT * FROM PRODUCTS WHERE url = %s", (url,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"[❌ ERROR fetch_product] {e}")
            self.connection.rollback()
            return None

    def close(self):
        try:
            self.connection.close()
        except Exception as e:
            print(f"[❌ ERROR close connection] {e}")

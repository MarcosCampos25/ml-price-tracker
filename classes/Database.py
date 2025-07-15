import psycopg2
import os

class Database:
    def __init__(self, _=None):
        self.connection = psycopg2.connect(
            dbname=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT"),
        )
        self.cursor = self.connection.cursor()

    def setup_database(self):
        self.create_table('PRODUCTS', {
            'url': 'TEXT PRIMARY KEY',
            'title': 'TEXT NOT NULL',
            'current_price': 'REAL NOT NULL',
            'last_price': 'REAL NOT NULL',
            'best_price': 'REAL NOT NULL',
            'last_revision': 'TIMESTAMP NOT NULL',
            'img': 'TEXT'
        })

    def create_table(self, table_name, columns):
        columns_with_types = ', '.join(f"{col} {typ}" for col, typ in columns.items())
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})")
        self.connection.commit()

    def insert_product(self, product):
        self.cursor.execute("""
            INSERT INTO PRODUCTS (url, title, current_price, last_price, best_price, last_revision, img)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            ON CONFLICT (url) DO NOTHING
        """, (
            product['url'], product['title'], product['current_price'],
            product['current_price'], product['current_price'], product.get('img', None)
        ))
        self.connection.commit()

    def delete_product(self, url):
        self.cursor.execute("DELETE FROM PRODUCTS WHERE url = %s", (url,))
        self.connection.commit()
        return self.cursor.rowcount > 0

    def update_product(self, product):
        self.cursor.execute("""
            UPDATE PRODUCTS
            SET current_price = %s, last_price = %s, best_price = %s, last_revision = NOW()
            WHERE url = %s
        """, (
            product['current_price'], product['last_price'],
            product['best_price'], product['url']
        ))
        self.connection.commit()

    def fetch_all_products(self):
        self.cursor.execute("SELECT * FROM PRODUCTS ORDER BY title DESC")
        return self.cursor.fetchall()

    def fetch_product(self, url):
        self.cursor.execute("SELECT * FROM PRODUCTS WHERE url = %s", (url,))
        return self.cursor.fetchone()

    def close(self):
        self.connection.close()

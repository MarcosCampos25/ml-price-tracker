import sqlite3

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row  # ⬅️ clave
        self.cursor = self.connection.cursor()

    def setup_database(self):
        self.create_table('PRODUCTS', {
            'url': 'TEXT PRIMARY KEY',
            'title': 'TEXT NOT NULL',
            'current_price': 'REAL NOT NULL',
            'last_price': 'REAL NOT NULL',
            'best_price': 'REAL NOT NULL',
            'last_revision': 'DATETIME NOT NULL',
            'img': 'TEXT'
        })

    def create_table(self, table_name, columns):
        columns_with_types = ', '.join(f"{col} {typ}" for col, typ in columns.items())
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types})")
        self.connection.commit()

    def insert_product(self, product):
        self.cursor.execute("""
            INSERT INTO PRODUCTS (url, title, current_price, last_price, best_price, last_revision, img)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
        """, (
            product['url'], product['title'], product['current_price'], product['current_price'], product['current_price'], product.get('img', None)
        ))
        self.connection.commit()
    
    def delete_product(self, url):
        self.cursor.execute("DELETE FROM PRODUCTS WHERE url = ?", (url,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def update_product(self, product):
        self.cursor.execute("""
            UPDATE PRODUCTS
            SET current_price = ?, last_price = ?, best_price = ?, last_revision = datetime('now')
            WHERE url = ?
        """, (product['current_price'], product['last_price'], product['best_price'], product['url']))
        self.connection.commit()
    
    def fetch_all_products(self):
        self.cursor.execute("SELECT * FROM PRODUCTS ORDER BY title DESC")
        return self.cursor.fetchall()

    def fetch_product(self, url):
        self.cursor.execute("SELECT * FROM PRODUCTS WHERE url = ?", (url,))
        return self.cursor.fetchone()

    def close(self):
        self.connection.close()
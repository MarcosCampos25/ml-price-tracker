from classes.Database import Database
from classes.MercadoLibre import MercadoLibre
from classes.Alerts import Alert

def track_all_products(programmed_task=False):
    template = "resume_products_pt.html" if programmed_task else "resume_products.html"
    al = Alert()
    db = Database('db/tracker.db')
    db.setup_database()


    ml = MercadoLibre()
    data = db.fetch_all_products()
    urls = [row['url'] for row in data]
    for url in urls:
        product_details = ml.get_product_details(url)
        actual_data = db.fetch_product(product_details['url'])
        if actual_data:
            product_details['last_price'] = actual_data[2]
            best_price = actual_data[4]
            
            if product_details['current_price'] < best_price:
                best_price = product_details['current_price']
                al.mail_alert_one_product(db, product_details, "new_best_price.html")
            
            db.update_product({
                'url': product_details['url'],
                'current_price': product_details['current_price'],
                'last_price': product_details['last_price'],
                'best_price': best_price,
            })
        else:
            db.insert_product(product_details)
    al.mail_alert_all_product(db, template)
    db.close()
    return True

def scrap_and_insert_new_product(url):
    db = Database('db/tracker.db')
    db.setup_database()
    ml = MercadoLibre()
    product_details = ml.get_product_details(url)
    db.insert_product(product_details)
    return True

if __name__ == "__main__":
    track_all_products()

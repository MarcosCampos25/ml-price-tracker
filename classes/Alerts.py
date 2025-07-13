from classes.Mail import Mail

class Alert:
    mail = Mail()

    def mail_alert_one_product(self, db, product_details, template):
        products = db.fetch_product(product_details['url'])
        
        self.mail.send_mail(
            to="marcoscampos3123@gmail.com",
            subject="Seguimiento de precio",
            template_name=template,
            context={"products": [products]},
            from_name="PriceTracker"
        )

    def mail_alert_all_product(self, db, template):
        products = db.fetch_all_products()
        
        self.mail.send_mail(
            to="marcoscampos3123@gmail.com",
            subject="Seguimiento de precio",
            template_name=template,
            context={"products": products},
            from_name="PriceTracker"
        )
import smtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
import os

class Mail:
    smtp_server = 'smtp.gmail.com'
    smtp_port= 465
    username= os.getenv("EMAIL_USERNAME")
    password= os.getenv("EMAIL_PASSWORD")
    env = Environment(loader=FileSystemLoader('templates'))

    def render_template(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)

    def send_mail(self, to, subject, template_name, context, from_name=None):
        # Render HTML
        html_content = self.render_template(template_name, context)

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = f"{from_name or self.username} <{self.username}>"
        msg['To'] = to
        msg.set_content("Este correo requiere un cliente compatible con HTML.")
        msg.add_alternative(html_content, subtype='html')

        # Send email
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as smtp:
            smtp.login(self.username, self.password)
            smtp.send_message(msg)
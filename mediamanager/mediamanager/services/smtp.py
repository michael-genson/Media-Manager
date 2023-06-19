from email.message import EmailMessage
from smtplib import SMTP


class SMTPService:
    def __init__(self, server: str, port: int, username: str, password: str, use_tls: bool = True) -> None:
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send(self, msg: EmailMessage) -> None:
        smtp = SMTP(self.server, port=self.port)

        smtp.ehlo()
        smtp.starttls()

        smtp.login(self.username, self.password)
        smtp.send_message(msg)

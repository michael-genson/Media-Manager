import asyncio
from email.message import EmailMessage

from aiosmtplib import SMTP


class SMTPService:
    def __init__(self, server: str, port: int, username: str, password: str, use_tls: bool = True) -> None:
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    async def send_all(self, msgs: list[EmailMessage]) -> None:
        smtp = SMTP(self.server, port=self.port)
        async with smtp:
            await smtp.login(self.username, self.password)
            await asyncio.gather(*[smtp.send_message(msg) for msg in msgs])

    async def send(self, msg: EmailMessage) -> None:
        return await self.send_all([msg])

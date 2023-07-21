import mimetypes
from datetime import datetime
from email.message import EmailMessage

from fastapi.templating import Jinja2Templates

from ..app import STATIC_DIR, settings

email_templates = Jinja2Templates(directory=f"{STATIC_DIR}/email_templates")


class EmailAttachment:
    def __init__(self, filename: str, filepath: str, mimetype: str | None = None) -> None:
        self.filename = filename
        self.filepath = filepath
        if not mimetype:
            mimetype, _ = mimetypes.guess_type(filepath)
            if not mimetype:
                raise ValueError("Cannot infer mimetype from file.")

        self.mimetype = mimetype


class GenericEmailTemplate:
    def __init__(self, template: str, is_html: bool = False) -> None:
        self.template = template
        self.is_html = is_html

    def message(
        self,
        subject: str,
        sender: str,
        recipients: str | list[str],
        cc: str | list[str] | None = None,
        bcc: str | list[str] | None = None,
        attachments: list[EmailAttachment] | None = None,
        **kwargs,
    ) -> EmailMessage:
        """Constructs a message to be sent via SMTP. Provide merge fields as kwargs"""

        if attachments is None:
            attachments = []

        body_template = email_templates.get_template(self.template)
        body = body_template.render(**kwargs)

        if isinstance(recipients, list):
            recipients = ", ".join(recipients)

        if isinstance(cc, list):
            cc = ", ".join(cc)

        if isinstance(bcc, list):
            bcc = ", ".join(bcc)

        msg = EmailMessage()
        if self.is_html:
            msg.set_content(body, subtype="html")

        else:
            msg.set_content(body)

        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipients
        msg["Cc"] = cc or ""
        msg["Bcc"] = bcc or ""

        for attachment in attachments:
            maintype, subtype = attachment.mimetype.split("/", 1)
            with open(attachment.filepath, "rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=attachment.filename)

        return msg


class ExpiredMediaEmail:
    def __init__(self) -> None:
        self.template = GenericEmailTemplate("expired_media.html", is_html=True)

    def message(
        self, sender_name: str, recipient_email: str, media_count: int, media_csv_filepath: str
    ) -> EmailMessage:
        subject = f"[{settings.app_title}] Expired Media Report"
        filename = f"expired_media_report_{datetime.today().date().isoformat()}.csv"

        return self.template.message(
            subject,
            sender=sender_name,
            recipients=recipient_email,
            attachments=[EmailAttachment(filename, media_csv_filepath, "text/csv")],
            # merge fields
            app_title=settings.app_title,
            recipient_name=f"{settings.app_title} admin",
            media_count=media_count,
        )


class ExpiredMediaEmailFailure:
    def __init__(self) -> None:
        self.template = GenericEmailTemplate("expired_media_failure.html", is_html=True)

    def message(
        self,
        sender_name: str,
        recipient_email: str,
    ) -> EmailMessage:
        subject = f"!! [{settings.app_title}] Expired Media Report Failure !!"
        return self.template.message(
            subject,
            sender=sender_name,
            recipients=recipient_email,
            # merge fields
            app_title=settings.app_title,
            recipient_name=f"{settings.app_title} admin",
        )

import smtplib
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self, smtp_server, smtp_port, email_user, email_pwd, receiver):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_user = email_user
        self.email_pwd = email_pwd
        self.receiver = receiver

    def send_email(self, subject, content):
        msg = MIMEText(content, "markdown", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.email_user
        msg["To"] = self.receiver

        # 连接smtp发送邮件
        server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        server.login(self.email_user, self.email_pwd)
        server.sendmail(self.email_user, self.receiver, msg.as_string())
        server.quit()

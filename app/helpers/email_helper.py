import smtplib, ssl

class EmailHelper():
    port = 587  # For starttls
    smtp_server = "smtp.gmail.com"
    sender_email = "alerts.cryptocoins@gmail.com"
    receiver_email = "ivanbevivino@gmail.com"
    a = "37752556"

    @classmethod
    def send(cls,message):
        msg =         msg = f"""\
Subject: AAVE ALERT 
To: {cls.receiver_email}
From: {cls.sender_email}


{message}"""
        context = ssl.create_default_context()
        with smtplib.SMTP(cls.smtp_server, cls.port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(cls.sender_email, cls.a)
            server.sendmail(cls.sender_email, cls.receiver_email, msg)
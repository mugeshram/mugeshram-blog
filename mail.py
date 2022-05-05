import  smtplib




class Mailer:
    def __init__(self):
        self.gmail = "testpython019@gmail.com"
        self.password = "g9%rc7&e9)mz"
        self.to_gmail = ""


    def send(self,message):
        """input message as Subject:jdjdhj'\n\n'content """
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=self.gmail, password=self.password)
            connection.sendmail(
                from_addr=self.gmail,
                to_addrs=self.to_gmail,
                msg=message

            )
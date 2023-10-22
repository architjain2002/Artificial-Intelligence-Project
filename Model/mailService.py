import smtplib

# creates SMTP session
s = smtplib.SMTP('smtp.gmail.com', 587)

# start TLS for security
s.starttls()

# Authentication
s.login("adigupta239@gmail.com", "mxwzguwzdcxcrqdw")

# message to be sent
subject = "Suspicious activity detected on your network"
text = 'Dear user, our model have detected some malicious traffic on your network which could be a possible attempt of a DDOS attack. You can perform the following action :\n \n 1.Disconnect all your devices from the network.\n 2.Check if any unknown software is installed on your device. \n 3.Contact a security personnel ASAP. \n  \nHope you find this alert helpful and took the action at right time.'

message = 'Subject: {}\n\n{}'.format(subject, text)

# sending the mail
s.sendmail("adigupta239@gmail.com", "arcyjain2002@gmail.com", message)

# terminating the session
s.quit()

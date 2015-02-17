import argparse
from ckan_util import logger

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

subject = 'Your OpenDataPhilly Account'

def get_msg(fromaddr, toaddr, username, url):
    """
    Generate a MIME compatible email body using the msg.txt file as a template.
    """
    with open('msg.txt', 'r') as f:
        msg = f.read()
    mimemsg = MIMEMultipart()
    mimemsg['From'] = fromaddr
    mimemsg['To'] = toaddr
    mimemsg['Subject'] = subject
    mimemsg.attach(MIMEText(msg.format(username=username,
                                       url=url,
                                       email=toaddr),
                            'plain'))
    return mimemsg.as_string()


def main():
    """
    Open the created_accounts.csv file that users2ckan.py creates and send
    password reset e-mails to the users.
    """
    parser = argparse.ArgumentParser(description='Send password reset email')
    parser.add_argument('--server', required=True)
    parser.add_argument('--port', required=True)
    parser.add_argument('--fromaddr', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--continueafter', default=False, help="continue after this username")
    parser.add_argument('--count', type=int, default=100, help="send this many emails")
    args = parser.parse_args()
    server = smtplib.SMTP(args.server, args.port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(args.fromaddr, args.password)
    with open('created_accounts.csv', 'r') as f:
        if args.continueafter:
            for line in f:
                (username, email, url) = line.strip().split(',')
                if args.continueafter == username:
                    break
        for n, line in enumerate(f, 1):
            if n > args.count:
                break
            (username, email, url) = line.strip().split(',')
            server.sendmail(args.fromaddr, email, get_msg(args.fromaddr,
                                                          email,
                                                          username,
                                                          url))
            print("{}/{} sent mail to {} / {}".format(n, args.count, username, email))


if __name__ == '__main__':
    main()

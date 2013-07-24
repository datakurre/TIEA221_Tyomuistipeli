# -*- coding: utf-8 -*-
import smtplib
import json
from email.mime.text import MIMEText

def email(addr, players):

    #print addr, players

    #fp = open(textfile, 'rb')
    # Create a text/plain message
    #msg = MIMEText(fp.read())
    #fp.close()

    link = 'http://työmuistipeli.fi/peli/#players='+json.dumps(players)

    msg = MIMEText("""
Hei,

Oheisella linkillä saat käyttöösi pelinappulat:

%(link)s


   Terveisin Lupu ja Lasse


""" % { 'link':link }, _charset="UTF-8")

    me = 'noreply@työmuistipeli.fi'
    msg['Subject'] = 'työmuistipeli.fi: pelinappulat'
    msg['From'] = me
    msg['To'] = addr

    s = smtplib.SMTP('siirappi.com')
    s.sendmail(me, [addr], msg.as_string())
    s.quit()

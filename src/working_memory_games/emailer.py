# -*- coding: utf-8 -*-
import smtplib
import json, urllib
from email.mime.text import MIMEText
from email.header import Header

# http://bugs.python.org/issue12552
from email import charset
charset.add_charset('utf-8', charset.SHORTEST, charset.QP)

def email(addr, players):

    #print addr, players


    link = ''
    for p in players:
        if link != '': 
            link += '&'
        link += 'player='+urllib.quote_plus(p['name'])+';'+p['id']
    link = 'http://työmuistipeli.fi/peli/#'+link

    msg = """
Hei,

Oheisella linkillä saat käyttöösi pelinappulat:

%(link)s


Terveisin Lupu ja Lasse


""" % { 'link':link }

    msg = MIMEText(msg, 'plain', 'utf-8')

    me = 'noreply@xn--tymuistipeli-5ib.fi'
    msg['Subject'] = Header('työmuistipeli.fi: pelinappulat', 'utf-8')
    msg['From'] = me
    msg['To'] = addr

    s = smtplib.SMTP('siirappi.com')
    s.sendmail(me, [addr], msg.as_string())
    s.quit()

Getting started
---------------

Tarvitaan Python 2.7.

Asennetaan kaikki tarvittavat ja asetetaan polut kohdalleen::

    python bootstrap.py
    bin/buildout
    source bin/activate

Annetaan supervisorin huolehtia ZEO-palvelimesta::

    supervisord

Palveluiden tila selviää::

    supervisorctl status

Käynnistetään Pyramid-sovellus edustalle kehitystilaan::

    pserve development.ini

Myöhemmin sovelluksen voi käynnistää taustalle tuotantotilaan (ja vielä
myöhemmin supervisor configuroidaan käynnistämään myös pyramid
automaattisesti)::

    supervisorctl start pyramid

Ja sammutetaan kaikki::

    supervisorctl shutdown

Nollataan tietokanta::

    supervisorctl shutdown
    bin/buildout -o install reset

Ja koskus ajetaan testit::

    bin/test

Myöhemmin voidaan pakata tietokantaa (ZEOn ollessa päällä)::

    bin/zeopack -u var/zeo.sock

Ja koska tahansa saada karkea yhteenveto sen sisältämistä olioista::

    bin/python parts/analyze.py

Lopuksi, tietokannan visuaalinen selaaminen onnistuu käynnistämällä ``eye``,
joko

    1. ZEOn ollessa päällä::

        bin/eye -p 8070 zeo://`pwd`/var/zeo.sock

    2. ZEOn ollessa sammutettuna::

        bin/eye -p 8070 var/filestorage/Data.fs

Molemmissa tapauksissa tietokanta löytyy osoitteesta http://localhost:8070/

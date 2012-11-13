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

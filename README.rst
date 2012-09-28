Getting started
---------------

Tarvitaan Python 2.7.

Asennetaan kaikki tarvittavat ja asetetaan polut kohdalleen::

    python bootstrap.py
    bin/buildout -c develop.cfg
    source bin/activate

Annetaan supervisorin huolehtia ZEO-palvelimesta::

    supervisord

Palveluiden tila selviää::

    supervisorctl status

Käynnistetään Pyramid-sovellus edustalle kehitystilaan::

    pserve development.ini

Myöhemmin sovelluksen voi käynnistää taustalle tuotantotilaan::

    supervisorctl start pyramid

Ja sammutetaan kaikki::

    supervisorctl shutdown

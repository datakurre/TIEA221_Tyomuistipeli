# -*- coding: utf-8
from bottle import route, run, static_file

import random, json
from StringIO import StringIO

@route('/')
@route('/index.html')
def index(): 
    return '''<!DOCTYPE html>
<html>
  <head>
    <title>Title of the document</title>
    <script type="text/javascript" charset="utf-8" src="js/lib/jquery.min.js"></script>
    <script type="text/javascript" charset="utf-8" src="js/browsertest.js"></script>
  </head>
  <body>
    <h1>Ty&ouml;muistitreenari</h1>
    <noscript>Valitettavasti javascript ei ole selaimestasi päällä.</noscript>
  </body>
</html>'''

@route('/game/<idx:int>')
def game(idx):
    if idx == 0:
        return '''<!DOCTYPE html>
<html>
  <head>
    <title>Autokisa</title>
    <link rel="stylesheet" type="text/css" href="/css/style.css" /> 
    <script type="text/javascript" charset="utf-8" src="/js/lib/jquery.min.js"></script>
    <script type="text/javascript" charset="utf-8" src="/js/game.js"></script>
    <script type="text/javascript" charset="utf-8" src="/js/racing.js"></script>
  </head>
  <body>
    <div id="game">
      <div id="level">
        Taso: 
        <span/>
      </div>
      <img src="/img/race/racing.jpg" alt=""/>
      <img id="car0" class="carmask" src="/img/race/mask1.png" alt=""/>
      <img id="car1" class="carmask" src="/img/race/mask2.png" alt=""/>
      <img id="car2" class="carmask" src="/img/race/mask3.png" alt=""/>
      <img id="car3" class="carmask" src="/img/race/mask1.png" alt=""/>
      <img id="car4" class="carmask" src="/img/race/mask3.png" alt=""/>
      <img id="car5" class="carmask" src="/img/race/mask2.png" alt=""/>
    </div>
  </body>
</html>'''
    else:
        return '''<!DOCTYPE html>
<html>
  <head>
    <title>Koneita</title>
    <link rel="stylesheet" type="text/css" href="/css/style.css" /> 
    <script type="text/javascript" charset="utf-8" src="/js/lib/jquery.min.js"></script>
    <script type="text/javascript" charset="utf-8" src="/js/game.js"></script>
    <script type="text/javascript" charset="utf-8" src="/js/machine.js"></script>
  </head>
  <body>
    <div id="game">
      <div id="level">
        Taso: 
        <span/>
      </div>
      <img src="/img/machine/kone.jpg" alt=""/>
      <img id="m0" class="machinemask" src="/img/machine/m1.png" alt=""/>
      <img id="m1" class="machinemask" src="/img/machine/m2.png" alt=""/>
      <img id="m2" class="machinemask" src="/img/machine/m3.png" alt=""/>
      <img id="m3" class="machinemask" src="/img/machine/m4.png" alt=""/>
      <img id="m4" class="machinemask" src="/img/machine/m5.png" alt=""/>
      <img id="m5" class="machinemask" src="/img/machine/m6.png" alt=""/>
      <img id="m6" class="machinemask" src="/img/machine/m7.png" alt=""/>
      <img id="m7" class="machinemask" src="/img/machine/m8.png" alt=""/>
      <img id="m8" class="machinemask" src="/img/machine/m9.png" alt=""/>
      <img id="b0" class="blink" src="/img/machine/blink.png" alt=""/>
      <img id="b1" class="blink" src="/img/machine/blink.png" alt=""/>
      <img id="b2" class="blink" src="/img/machine/blink.png" alt=""/>
      <img id="b3" class="blink" src="/img/machine/blink.png" alt=""/>
      <img id="b4" class="blink" src="/img/machine/blink.png" alt=""/>
      <img id="b5" class="blink" src="/img/machine/blink.png" alt=""/>
      <img id="b6" class="blink" src="/img/machine/blink.png" alt=""/>
      <img id="b7" class="blink" src="/img/machine/blink.png" alt=""/>
      <img id="b8" class="blink" src="/img/machine/blink.png" alt=""/>
    </div>
  </body>
</html>'''


# REST API
# ========

@route('/rest/get/game/<game:int>/user/<uid>')
def game(game, uid): 
    # sample new game, depends of game whether same number can be reselected
    level = get_level(uid)
    io = StringIO()
    if game == 0:
        count = 6
    elif game == 1:
        count = 9
    items = random.sample(range(count)*2, level)
    if level <= count:
        items = random.sample(range(count), level)
    json.dump({ 
            'items': items,
            'level': get_level(uid)
            }, io)
    return io.getvalue()

@route('/rest/game/done/user/<uid>')
def game_done(uid):
    level[uid] += 0.5

    return """
<div id="overlay">
  <div id="shader"/>
  <div id="dialog">
    <h2>Hienoa!</h2>
    <a id="next" href="#">
      Seuraava peli
    </a>
  </div>
</div>
"""

@route('/rest/game/incorrect/user/<uid>')
def game_incorrect(uid):
    level[uid] -= 0.5
    if level[uid] < 2:
        level[uid] = 2

    return """
<div id="overlay">
  <div id="shader"/>
  <div id="dialog">
    <h2>Ei onnistunut</h2>
    <a id="next" href="#">
      Kokeile uudelleen
    </a>
  </div>
</div>
"""

global level
level = {}

def get_level(uid): 
    if not uid in level:
        level[uid] = 3
    return int(level[uid])


@route('/list.html')
def list(): return """<!DOCTYPE html>
<html>
  <head>
    <title>Title of the document</title>
  </head>
  <body>
    <h1>Ty&ouml;muisti treenari</h1>
    <ul>
      <li><a href="4x4.html">4x4</a></li>
      <li><a href="numbers.html">Numeroiden toistaminen</a></li>
      <li><a href="birds.html">Kurkiaura</a></li>
    </ul>
  </body>
</html>"""

@route('/js/<file:path>')
def static_js(file):
    return static_file(file, root='./src/js')

@route('/img/<file:path>')
def static_img(file):
    return static_file(file, root='./src/img')

@route('/css/<file:path>')
def static_css(file):
    return static_file(file, root='./src/css')

@route('/favicon.ico')
def icon():
    return static_img('favicon.ico')


run(host='localhost', port=8080, reloader=True)

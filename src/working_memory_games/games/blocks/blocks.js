(function() {
  var Circle, DEBUG, Entity, FPS, Rectangle, SCALE, Stage, StaticCircle, StaticRectangle, b2AABB, b2Body, b2BodyDef, b2CircleShape, b2DebugDraw, b2Fixture, b2FixtureDef, b2MassData, b2PolygonShape, b2Vec2, b2World, getBoundingBox, grepFloat,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
    __slice = Array.prototype.slice;

  FPS = 15;

  SCALE = 30;

  DEBUG = false;

  window.requestAnimFrame = (function() {
    return window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame || function(callback, element) {
      return window.setTimeout(callback, 1000 / FPS);
    };
  })();

  grepFloat = function(needle) {
    return parseFloat(typeof needle.match === "function" ? needle.match(/[-\d\.]+/) : void 0, 10) || 0.0;
  };

  getBoundingBox = function(body) {
    var aabb, fixture;
    aabb = new b2AABB();
    aabb.lowerBound = new b2Vec2(9999, 9999);
    aabb.upperBound = new b2Vec2(-9999, -9999);
    fixture = body.GetFixtureList();
    while (fixture) {
      aabb.Combine(aabb, fixture.GetAABB());
      fixture = fixture.GetNext();
    }
    return aabb;
  };

  b2Vec2 = Box2D.Common.Math.b2Vec2;

  b2BodyDef = Box2D.Dynamics.b2BodyDef;

  b2Body = Box2D.Dynamics.b2Body;

  b2FixtureDef = Box2D.Dynamics.b2FixtureDef;

  b2Fixture = Box2D.Dynamics.b2Fixture;

  b2World = Box2D.Dynamics.b2World;

  b2MassData = Box2D.Collision.Shapes.b2MassData;

  b2PolygonShape = Box2D.Collision.Shapes.b2PolygonShape;

  b2CircleShape = Box2D.Collision.Shapes.b2CircleShape;

  b2AABB = Box2D.Collision.b2AABB;

  b2DebugDraw = Box2D.Dynamics.b2DebugDraw;

  Entity = (function() {

    Entity.prototype.type = b2Body.b2_dynamicBody;

    function Entity(id, x, y, angle) {
      this.id = id;
      this.x = x;
      this.y = y;
      this.angle = angle != null ? angle : 0;
      this.el = window.document.createElement('div');
      this.el.id = this.id;
      this.el.className = 'box2d';
    }

    Entity.prototype.b2FixtureDef = function() {
      var fixture;
      fixture = new b2FixtureDef();
      fixture.density = 1.0;
      fixture.friction = 0.2;
      fixture.restitution = 0.2;
      return fixture;
    };

    Entity.prototype.b2BodyDef = function() {
      var body;
      body = new b2BodyDef();
      body.type = this.type;
      body.userData = this.id;
      body.position.x = this.x / SCALE;
      body.position.y = this.y / SCALE;
      body.angle = this.angle * Math.PI / 180;
      return body;
    };

    Entity.prototype.update = function(state) {
      this.x = state.x * SCALE;
      this.y = state.y * SCALE;
      this.angle = state.a * 180 / Math.PI;
      this.el.style.position = 'absolute';
      this.el.style['-webkit-transform'] = "rotate(" + state.a + "rad)";
      this.el.style['-moz-transform'] = "rotate(" + state.a + "rad)";
      this.el.style['-o-transform'] = "rotate(" + state.a + "rad)";
      return this.el.style['transform'] = "rotate(" + state.a + "rad)";
    };

    return Entity;

  })();

  Circle = (function(_super) {

    __extends(Circle, _super);

    function Circle(id, x, y, radius) {
      this.radius = radius;
      Circle.__super__.constructor.call(this, id, x, y);
      this.el.className += ' circle';
      this.el.style.borderRadius = "" + (this.radius * 0.1) + "em";
    }

    Circle.prototype.b2FixtureDef = function() {
      var fixture;
      fixture = Circle.__super__.b2FixtureDef.call(this);
      fixture.shape = new b2CircleShape(this.radius / SCALE);
      return fixture;
    };

    Circle.prototype.b2BodyDef = function() {
      var body;
      body = Circle.__super__.b2BodyDef.call(this);
      body.position.x = (this.x + this.radius) / SCALE;
      body.position.y = (this.y + this.radius) / SCALE;
      return body;
    };

    Circle.prototype.update = function(state) {
      var bottom, height, left, width;
      Circle.__super__.update.call(this, state);
      this.x = state.x * SCALE - this.radius;
      this.y = state.y * SCALE - this.radius;
      width = this.radius * 2 * 0.1;
      height = this.radius * 2 * 0.1 + 0.01;
      left = this.x * 0.1;
      bottom = this.y * 0.1;
      this.el.style.width = "" + (Math.round(width * 1000) / 1000) + "em";
      this.el.style.height = "" + (Math.round(height * 1000) / 1000) + "em";
      this.el.style.left = "" + (Math.round(left * 1000) / 1000) + "em";
      return this.el.style.bottom = "" + (Math.round(bottom * 1000) / 1000) + "em";
    };

    return Circle;

  })(Entity);

  StaticCircle = (function(_super) {

    __extends(StaticCircle, _super);

    StaticCircle.prototype.type = b2Body.b2_staticBody;

    function StaticCircle(id, x, y, width, height) {
      StaticCircle.__super__.constructor.call(this, id, x, y, width, height);
      this.el.className += ' static';
    }

    return StaticCircle;

  })(Circle);

  Rectangle = (function(_super) {

    __extends(Rectangle, _super);

    function Rectangle(id, x, y, width, height) {
      this.width = width;
      this.height = height;
      Rectangle.__super__.constructor.call(this, id, x, y);
      this.el.className += ' rectangle';
    }

    Rectangle.prototype.b2FixtureDef = function() {
      var fixture;
      fixture = Rectangle.__super__.b2FixtureDef.call(this);
      fixture.shape = new b2PolygonShape();
      fixture.shape.SetAsBox(this.width / 2 / SCALE, this.height / 2 / SCALE);
      return fixture;
    };

    Rectangle.prototype.b2BodyDef = function() {
      var body;
      body = Rectangle.__super__.b2BodyDef.call(this);
      body.position.x = (this.x + this.width / 2) / SCALE;
      body.position.y = (this.y + this.height / 2) / SCALE;
      return body;
    };

    Rectangle.prototype.update = function(state) {
      var bottom, height, left, width;
      Rectangle.__super__.update.call(this, state);
      this.x = state.x * SCALE - this.width / 2;
      this.y = state.y * SCALE - this.height / 2;
      width = this.width * 0.1;
      height = this.height * 0.1 + 0.01;
      left = this.x * 0.1;
      bottom = this.y * 0.1;
      this.el.style.width = "" + (Math.round(width * 1000) / 1000) + "em";
      this.el.style.height = "" + (Math.round(height * 1000) / 1000) + "em";
      this.el.style.left = "" + (Math.round(left * 1000) / 1000) + "em";
      return this.el.style.bottom = "" + (Math.round(bottom * 1000) / 1000) + "em";
    };

    return Rectangle;

  })(Entity);

  StaticRectangle = (function(_super) {

    __extends(StaticRectangle, _super);

    StaticRectangle.prototype.type = b2Body.b2_staticBody;

    function StaticRectangle(id, x, y, width, height) {
      StaticRectangle.__super__.constructor.call(this, id, x, y, width, height);
      this.el.className += ' static';
    }

    return StaticRectangle;

  })(Rectangle);

  Stage = (function() {

    function Stage(root, width, height, gravity) {
      var canvas, debugDraw;
      this.root = root;
      this.width = width;
      this.height = height;
      if (gravity == null) gravity = 10;
      this.world = new b2World(new b2Vec2(0, gravity * -1), true);
      this.entities = {};
      this.bodies = {};
      this.callbacks = [];
      this.animating = false;
      if (DEBUG) {
        canvas = window.document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        this.root.appendChild(canvas);
        debugDraw = new b2DebugDraw();
        debugDraw.SetSprite(canvas.getContext('2d'));
        debugDraw.SetDrawScale(SCALE);
        debugDraw.SetFillAlpha(0.3);
        debugDraw.SetLineThickness(1.0);
        debugDraw.SetFlags(b2DebugDraw.e_shapeBit | b2DebugDraw.e_jointBit);
        this.world.SetDebugDraw(debugDraw);
      }
    }

    Stage.prototype.applyEntity = function() {
      var body, entity, fixture, fixtures, _i, _len;
      entity = arguments[0], fixtures = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
      body = this.world.CreateBody(entity.b2BodyDef());
      for (_i = 0, _len = fixtures.length; _i < _len; _i++) {
        fixture = fixtures[_i];
        body.CreateFixture(fixture);
      }
      if (!fixtures.length) body.CreateFixture(entity.b2FixtureDef());
      this.entities[entity.id] = entity;
      this.bodies[entity.id] = body;
      this.root.appendChild(entity.el);
      entity.update({
        x: body.GetPosition().x,
        y: body.GetPosition().y,
        a: body.GetAngle()
      });
      return this;
    };

    Stage.prototype.resetWorld = function() {
      var body, entity, id, _ref, _ref2;
      _ref = this.entities;
      for (id in _ref) {
        entity = _ref[id];
        this.root.removeChild(entity.el);
        delete this.entities[id];
      }
      _ref2 = this.bodies;
      for (id in _ref2) {
        body = _ref2[id];
        this.world.DestroyBody(body);
        delete this.bodies[id];
      }
      return this;
    };

    Stage.prototype.resetViewport = function() {
      this.root.style.fontSize = "";
      this.root.style.right = "";
      this.root.style.bottom = "";
      this.root.style.left = "";
      return this;
    };

    Stage.prototype.applyImpulse = function(id, degrees, power) {
      var body, vector;
      vector = new b2Vec2(Math.cos(degrees * Math.PI / 180) * power, Math.sin(degrees * Math.PI / 180) * power);
      body = this.bodies[id];
      body.ApplyImpulse(vector, body.GetWorldCenter());
      return this;
    };

    Stage.prototype.setViewportCenter = function(x, y) {
      var bottom, left, right, scale;
      scale = grepFloat(this.root.style.fontSize) || 1.0;
      right = ((scale - 1) * this.width * -0.05) / scale;
      bottom = ((scale - 1) * this.height * -0.05) / scale;
      left = ((scale - 1) * this.width * -0.05) / scale;
      right = (this.width / 2 - x) * -0.1 + right;
      bottom = (this.height / 2 - y) * 0.1 + bottom;
      left = (this.width / 2 - x) * 0.1 + left;
      this.root.style.top = "" + (Math.round(top * 1000) / 1000) + "em";
      this.root.style.bottom = "" + (Math.round(bottom * 1000) / 1000) + "em";
      this.root.style.left = "" + (Math.round(left * 1000) / 1000) + "em";
      return this;
    };

    Stage.prototype.setViewportScale = function(scale) {
      var bottom, left, oldScale, right;
      oldScale = grepFloat(this.root.style.fontSize) || 1.0;
      right = ((oldScale - 1) * this.width * -0.05) / oldScale;
      bottom = ((oldScale - 1) * this.height * -0.05) / oldScale;
      left = ((oldScale - 1) * this.width * -0.05) / oldScale;
      right = grepFloat(this.root.style.right) - right;
      bottom = grepFloat(this.root.style.bottom) - bottom;
      left = grepFloat(this.root.style.left) - left;
      right = ((scale - 1) * this.width * -0.05) / scale + right;
      bottom = ((scale - 1) * this.height * -0.05) / scale + bottom;
      left = ((scale - 1) * this.width * -0.05) / scale + left;
      this.root.style.fontSize = "" + scale + "em";
      this.root.style.right = "" + (Math.round(right * 1000) / 1000) + "em";
      this.root.style.bottom = "" + (Math.round(bottom * 1000) / 1000) + "em";
      this.root.style.left = "" + (Math.round(left * 1000) / 1000) + "em";
      return this;
    };

    Stage.prototype.pan = function(from, to, seconds, callback, frame) {
      var coords, factor, x, y,
        _this = this;
      if (frame == null) frame = 0;
      factor = $.easing.swing(frame / (seconds * FPS));
      coords = this.getViewportCenter();
      x = from.x + (to.x - from.x) * factor;
      y = from.y + (to.y - from.y) * factor;
      this.setViewportCenter(x, y);
      if (x !== to.x || y !== to.y) {
        return requestAnimFrame(function() {
          return _this.pan(from, to, seconds, callback, frame + 1);
        });
      } else {
        return typeof callback === "function" ? callback() : void 0;
      }
    };

    Stage.prototype.zoom = function(from, to, seconds, callback, frame) {
      var factor, value,
        _this = this;
      if (frame == null) frame = 0;
      factor = $.easing.swing(frame / (seconds * FPS));
      value = from + (to - from) * factor;
      this.setViewportScale(value);
      if (factor < 1) {
        return requestAnimFrame(function() {
          return _this.zoom(from, to, seconds, callback, frame + 1);
        });
      } else {
        return typeof callback === "function" ? callback() : void 0;
      }
    };

    Stage.prototype.animate = function(callback) {
      var bbox, body, done, id, state, tmp, type,
        _this = this;
      if (typeof callback === 'function') this.callbacks.push(callback);
      if (this.animating && callback !== false) return this;
      this.world.Step(1 / FPS, 10, 10);
      this.world.ClearForces();
      body = this.world.GetBodyList();
      while (body) {
        id = typeof body.GetUserData === "function" ? body.GetUserData() : void 0;
        if (id) {
          state = {
            x: body.GetPosition().x,
            y: body.GetPosition().y,
            a: body.GetAngle() * -1
          };
          this.entities[id].update(state);
        }
        body = body.GetNext();
      }
      done = true;
      body = this.world.GetBodyList();
      while (body) {
        id = typeof body.GetUserData === "function" ? body.GetUserData() : void 0;
        type = typeof body.GetType === "function" ? body.GetType() : void 0;
        if (id && type !== b2Body.b2_staticBody) {
          bbox = getBoundingBox(body);
          if (bbox.upperBound.y < 0) this.world.DestroyBody(body);
        }
        if (type !== b2Body.b2_staticBody && body.IsAwake()) done = false;
        body = body.GetNext();
      }
      if (DEBUG) this.world.DrawDebugData();
      if (done) {
        tmp = [];
        this.animating = false;
        while (this.callbacks.length > 0) {
          tmp.push(this.callbacks.shift());
        }
        while (tmp.length > 0) {
          tmp.shift()();
        }
      } else {
        this.animating = true;
        requestAnimFrame(function() {
          return _this.animate(false);
        });
      }
      return this;
    };

    return Stage;

  })();

  jQuery(function($) {
    var $board, $dialer, $game, $query, $tower, answerWrong, applyCube, applyDialerCube, bg, cubeSize, dialer, fg, idx, initGame, newGame, newOrAnimGame, queueAppend, queueApplyImpulse, queueFadeIn, queueFadeOut, runAnimation;
    $game = $('#game');
    $board = $('#board');
    $tower = $('#tower');
    bg = new Stage($tower[0], $tower.width(), $tower.height());
    fg = new Stage($tower[0], $tower.width(), $tower.height());
    window.bg = bg;
    $dialer = $('#dialer').css({
      opacity: "0"
    });
    dialer = new Stage($dialer[0], $dialer.width(), $dialer.height(), -10);
    dialer.applyEntity(new StaticRectangle('dialer-floor', 0, 51, dialer.width, 1));
    applyDialerCube = function(idx) {
      var $dialCube, $number, dialCube, left;
      left = dialer.width / 2 - (60 * 9 / 2);
      dialCube = new Rectangle("dial-" + idx, left + 70 * (idx - 1), 0, 60, 60);
      dialCube.el.className += " color-" + idx;
      dialer.applyEntity(dialCube);
      $dialCube = $(dialCube.el);
      $number = $("<span class=\"number number-" + idx + "\">" + idx + "</span>");
      $number.appendTo($dialCube);
      return $dialCube.click(function() {
        var cube, currentIdx, id, item, items, size;
        dialer.applyImpulse("dial-" + idx, 90, 40);
        dialer.animate();
        item = idx;
        items = global.gameItems;
        currentIdx = global.userItems.length;
        size = cubeSize(bg, items.length);
        if (items[currentIdx] === item) {
          id = "fg-cube-" + currentIdx;
          left = fg.width / 2 - size / 2;
          cube = new Rectangle(id, left, fg.height, size, size);
          fg.applyEntity(cube);
          cube.el.className += " color-" + item;
          $number = $("<span class=\"number\">" + item + "</span>");
          $number.appendTo($(cube.el));
          $number.css('font-size', Math.floor(size / 10) + 'em');
          $('body').append('<div class="modal-backdrop curtain"></div>');
          $game.queue(function() {
            return fg.animate(function() {
              return $game.dequeue();
            });
          });
          if (currentIdx + 1 === items.length) {
            bg.resetWorld();
            $game.queue(function() {
              $board.animate({
                bottom: "0em"
              }, 1000);
              return $dialer.animate({
                bottom: "-7em",
                opacity: "0"
              }, 1000, function() {
                return $game.dequeue();
              });
            });
            $game.queue(function() {
              fg.applyImpulse("fg-cube-0", -180, 15 * items.length);
              fg.applyImpulse("fg-cube-1", -0, 20 * items.length);
              return fg.animate(function() {
                return $game.dequeue();
              });
            });
          } else {
            $game.queue(function() {
              return $("#bg-cube-" + (currentIdx + 1)).addClass("placeholder").fadeIn(0, function() {
                return $game.dequeue();
              });
            });
          }
          return $game.queue(function() {
            $('.modal-backdrop.curtain').remove();
            GameCheckUserPress(item);
            return $game.dequeue();
          });
        } else {
          return GameCheckUserPress(item);
        }
      });
    };
    for (idx = 1; idx <= 9; idx++) {
      applyDialerCube(idx);
    }
    cubeSize = function(stage, count) {
      return Math.min(100, stage.height * .9 / count);
    };
    applyCube = function(stage, id, position, count) {
      var cube, left, size;
      size = cubeSize(stage, count);
      left = stage.width / 2 - size / 2;
      cube = new Rectangle(id, left, 0 + size * 1.05 * position, size, size);
      stage.applyEntity(cube);
      $(cube.el).addClass('white').css('border-width', size / 100 + 'em');
      return cube;
    };
    queueAppend = function($cube, $el, size) {
      $game.queue(function() {
        $el.appendTo($cube);
        $el.css('font-size', Math.floor(size / 10) + 'em');
        return $game.dequeue();
      });
      return $game;
    };
    queueFadeIn = function($el) {
      $game.queue(function() {
        $el.removeClass('white');
        return $game.dequeue();
      });
      return $game;
    };
    queueFadeOut = function($el) {
      $game.queue(function() {
        return $el.fadeOut(1000, function() {
          return $game.dequeue();
        });
      });
      return $game;
    };
    queueApplyImpulse = function(stage, id, degrees, power) {
      $game.queue(function() {
        stage.applyImpulse(id, degrees, power);
        return $game.dequeue();
      });
      return $game;
    };
    initGame = function(data) {
      var $number, cube, idx, _ref, _ref2;
      $('body').append('<div class="modal-backdrop curtain"></div>');
      $('#level span').text(data.level);
      $board.css({
        bottom: "0"
      });
      $dialer.css({
        bottom: "-6em",
        opacity: "0"
      });
      bg.resetWorld().resetViewport().applyEntity(new StaticRectangle('bg-floor', -bg.width, -1, bg.width * 3, 1));
      fg.resetWorld().resetViewport().applyEntity(new StaticRectangle('fg-floor', -fg.width, -1, fg.width * 3, 1));
      for (idx = 0, _ref = data.items.length; 0 <= _ref ? idx < _ref : idx > _ref; 0 <= _ref ? idx++ : idx--) {
        cube = applyCube(bg, "bg-cube-" + idx, idx, data.items.length);
        cube.el.className += " color-" + data.items[idx];
      }
      $game.queue(function() {
        return bg.animate(function() {
          return $game.dequeue();
        });
      });
      for (idx = _ref2 = data.items.length - 1; _ref2 <= 0 ? idx <= 0 : idx >= 0; _ref2 <= 0 ? idx++ : idx--) {
        $number = $("<span class=\"number\">" + data.items[idx] + "</span>");
        queueFadeIn($("#bg-cube-" + idx));
        cube = queueAppend($("#bg-cube-" + idx), $number, cubeSize(bg, data.items.length));
        if (data.assisted) {
          if ((-idx + data.items.length - 1) % 3 === 2) {
            cube.delay(1500);
          } else {
            cube.delay(750);
          }
        } else {
          cube.delay(1000);
        }
        queueFadeOut($("#bg-cube-" + idx));
      }
      $game.queue(function() {
        $board.animate({
          bottom: "6em"
        }, 1000);
        $("#bg-cube-0").addClass("placeholder").fadeIn(1000);
        return $dialer.animate({
          opacity: "1",
          bottom: "0"
        }, 1000, function() {
          return $game.dequeue();
        });
      });
      return $game.queue(function() {
        $('.modal-backdrop.curtain').remove();
        return $game.dequeue();
      });
    };
    answerWrong = function(right, item, continueFunc) {
      return $('#dialer #dial-' + right).animate({
        opacity: 0
      }, 500).animate({
        opacity: 1
      }, 500).animate({
        opacity: 0
      }, 500).animate({
        opacity: 1
      }, 500).promise().done(continueFunc);
    };
    newGame = function() {
      $.preload('yrita', global.ctx + '/snd/yrita_rakentaa.[mp3,ogg]');
      return $('body').one('preloaded', function() {
        return $('body').play('yrita').promise().done(function() {
          return $.get('new', function(data) {
            GameInitialize(data.items, {
              newGame: newGame,
              answerWrong: answerWrong
            });
            return initGame(data);
          });
        });
      });
    };
    runAnimation = function() {
      var $someLeft, $someRight;
      $.preload('clip', global.base_ctx + '/snd/Pelit_ja_Pensselit_by_Ahti_Laine_clip_6s.[ogg,mp3]');
      $('body').one('preloaded', function() {
        return $('body').play('clip');
      });
      $('#animation').css('display', 'block');
      $someRight = 1000;
      $('#b3').animate({
        left: '46px'
      }, $someRight);
      $('#b4').animate({
        left: '85px'
      }, $someRight);
      $('#harakka').animate({
        left: '47px'
      }, $someRight);
      $someLeft = 900;
      $('#b3').animate({
        left: '30px'
      }, $someLeft);
      $('#b4').animate({
        left: '14px'
      }, $someLeft);
      $('#harakka').animate({
        left: '-37px'
      }, $someLeft);
      $someRight = 800;
      $('#b3').animate({
        left: '46px'
      }, $someRight);
      $('#b4').animate({
        left: '85px'
      }, $someRight);
      $('#harakka').animate({
        left: '47px'
      }, $someRight);
      $someLeft = 700;
      $('#b3').animate({
        left: '30px'
      }, $someLeft);
      $('#b4').animate({
        left: '14px'
      }, $someLeft);
      $('#harakka').animate({
        left: '-37px'
      }, $someLeft);
      $someRight = 600;
      $('#b3').animate({
        left: '46px'
      }, $someRight);
      $('#b4').animate({
        left: '85px'
      }, $someRight);
      $('#harakka').animate({
        left: '47px'
      }, $someRight);
      $someLeft = 500;
      $('#b3').animate({
        left: '30px'
      }, $someLeft);
      $('#b4').animate({
        left: '-14px'
      }, $someLeft);
      $('#harakka').animate({
        left: '-47px'
      }, $someLeft);
      $someLeft = 1000;
      $('#b3').animate({
        left: '20px'
      }, $someLeft);
      $('#b4').animate({
        left: '-700px',
        top: '400px'
      }, $someLeft);
      $('#harakka').animate({
        left: '-337px',
        top: '800px'
      }, $someLeft);
      return $('#b3,#b4,#harakka').promise().done(function() {
        $("#animation").hide();
        return newGame();
      });
    };
    $query = location.search !== void 0 ? location.search : '';
    newOrAnimGame = function() {
      return $.get('runanimation' + $query, function(data) {
        console.log('neworanim', data.animation);
        if (data.animation) {
          return runAnimation();
        } else {
          return newGame();
        }
      });
    };
    return newOrAnimGame();
  });

}).call(this);

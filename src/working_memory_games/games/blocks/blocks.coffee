# This will set the FPS for Box2D animation
FPS = 15

# This will scale Box2D physics model to pixels
SCALE = 30

# This will enable or disable debug mode
DEBUG = false

# This will define window.requestAnimFrame for all browsers.
# See: http://paulirish.com/2011/requestanimationframe-for-smart-animating/
window.requestAnimFrame = do ->
    window.requestAnimationFrame or
    window.webkitRequestAnimationFrame or
    window.mozRequestAnimationFrame or
    window.oRequestAnimationFrame or
    window.msRequestAnimationFrame or
    (callback, element) -> window.setTimeout(callback, 1000 / FPS)

# This helps parsing float values form style attributes
grepFloat = (needle) -> parseFloat(needle.match?(/[-\d\.]+/), 10) or 0.0

# This helps calculating bounding box for bodies
getBoundingBox = (body) ->
    aabb = new b2AABB()
    aabb.lowerBound = new b2Vec2(9999, 9999)
    aabb.upperBound = new b2Vec2(-9999, -9999)
    fixture = body.GetFixtureList()
    while fixture
        aabb.Combine(aabb, fixture.GetAABB())
        fixture = fixture.GetNext()
    return aabb

# These will define practical aliases for Box2D methods
b2Vec2 = Box2D.Common.Math.b2Vec2
b2BodyDef = Box2D.Dynamics.b2BodyDef
b2Body = Box2D.Dynamics.b2Body
b2FixtureDef = Box2D.Dynamics.b2FixtureDef
b2Fixture = Box2D.Dynamics.b2Fixture
b2World = Box2D.Dynamics.b2World
b2MassData = Box2D.Collision.Shapes.b2MassData
b2PolygonShape = Box2D.Collision.Shapes.b2PolygonShape
b2CircleShape = Box2D.Collision.Shapes.b2CircleShape
b2AABB = Box2D.Collision.b2AABB
b2DebugDraw = Box2D.Dynamics.b2DebugDraw

# These classes define the base basic Box2D entity wrappers for DOM.
# The most notable weirdness is that we want to flip the y-axis so that
# when (0, 0) is the top left corner of Box2D world, it is rendered as
# bottom left corner in DOM. (To ease building things from bottom to up.)

class Entity

    type: b2Body.b2_dynamicBody

    constructor: (@id, @x, @y, @angle=0) ->
        @el = window.document.createElement('div')
        @el.id = @id
        @el.className = 'box2d'

    b2FixtureDef: ->
        fixture = new b2FixtureDef()
        fixture.density = 1.0
        fixture.friction = 0.2
        fixture.restitution = 0.2  # 'bounciness'
        return fixture

    b2BodyDef: ->
        body = new b2BodyDef()
        body.type = @type
        body.userData = @id
        body.position.x = @x / SCALE
        body.position.y = @y / SCALE
        body.angle = @angle * Math.PI / 180
        return body

    update: (state) ->
        @x = state.x * SCALE
        @y = state.y * SCALE
        @angle = state.a * 180 / Math.PI

        @el.style.position = 'absolute'
        @el.style['-webkit-transform'] = "rotate(#{state.a}rad)"
        @el.style['-moz-transform'] = "rotate(#{state.a}rad)"
        @el.style['-o-transform'] = "rotate(#{state.a}rad)"
        @el.style['transform'] = "rotate(#{state.a}rad)"


class Circle extends Entity

    constructor: (id, x, y, @radius) ->
        super(id, x, y)
        @el.className += ' circle'
        @el.style.borderRadius = "#{@radius * 0.1}em"

    b2FixtureDef: ->
        fixture = super()
        fixture.shape = new b2CircleShape @radius / SCALE
        return fixture

    b2BodyDef: ->
        body = super()
        body.position.x = (@x + @radius) / SCALE
        body.position.y = (@y + @radius) / SCALE
        return body

    update: (state) ->
        super(state)

        @x = state.x * SCALE - @radius
        @y = state.y * SCALE - @radius

        width = @radius * 2 * 0.1
        height = @radius * 2 * 0.1 + 0.01  # 0.01 for rounding issues
        left = @x * 0.1
        bottom = @y * 0.1

        @el.style.width = "#{Math.round(width * 1000) / 1000}em"
        @el.style.height = "#{Math.round(height * 1000) / 1000}em"
        @el.style.left = "#{Math.round(left * 1000) / 1000}em"
        @el.style.bottom = "#{Math.round(bottom * 1000) / 1000}em"


class StaticCircle extends Circle

    type: b2Body.b2_staticBody

    constructor: (id, x, y, width, height) ->
        super(id, x, y, width, height)
        @el.className += ' static'


class Rectangle extends Entity

    constructor: (id, x, y, @width, @height) ->
        super(id, x, y)
        @el.className += ' rectangle'

    b2FixtureDef: ->
        fixture = super()
        fixture.shape = new b2PolygonShape()
        fixture.shape.SetAsBox(@width / 2 / SCALE, @height / 2 / SCALE)
        return fixture

    b2BodyDef: ->
        body = super()
        body.position.x = (@x + @width / 2) / SCALE
        body.position.y = (@y + @height / 2) / SCALE
        return body

    update: (state) ->
        super(state)

        @x = state.x * SCALE - @width / 2
        @y = state.y * SCALE - @height / 2

        width = @width * 0.1
        height = @height * 0.1 + 0.01  # 0.01 for rounding issues
        left = @x * 0.1
        bottom = @y * 0.1

        @el.style.width = "#{Math.round(width * 1000) / 1000}em"
        @el.style.height = "#{Math.round(height * 1000) / 1000}em"
        @el.style.left = "#{Math.round(left * 1000) / 1000}em"
        @el.style.bottom = "#{Math.round(bottom * 1000) / 1000}em"


class StaticRectangle extends Rectangle

    type: b2Body.b2_staticBody

    constructor: (id, x, y, width, height) ->
        super(id, x, y, width, height)
        @el.className += ' static'


class Stage

    constructor: (@root, @width, @height, gravity=10) ->
        # Note, how we define "reverse gravity" to "flip the y-axis".
        @world = new b2World(new b2Vec2(0, gravity * -1), true)  # sleep = true
        @entities = {}
        @bodies = {}

        @callbacks = []
        @animating = false

        if DEBUG
            canvas = window.document.createElement('canvas')
            canvas.width = @width
            canvas.height = @height
            @root.appendChild(canvas)

            debugDraw = new b2DebugDraw()
            debugDraw.SetSprite(canvas.getContext('2d'))
            debugDraw.SetDrawScale(SCALE)
            debugDraw.SetFillAlpha(0.3)
            debugDraw.SetLineThickness(1.0)
            debugDraw.SetFlags(b2DebugDraw.e_shapeBit | b2DebugDraw.e_jointBit)
            @world.SetDebugDraw(debugDraw)

    applyEntity: (entity, fixtures...) ->
        body = @world.CreateBody(entity.b2BodyDef())

        for fixture in fixtures
            body.CreateFixture(fixture)
        if not fixtures.length
            body.CreateFixture(entity.b2FixtureDef())

        @entities[entity.id] = entity
        @bodies[entity.id] = body

        @root.appendChild(entity.el)
        entity.update x: body.GetPosition().x, \
                      y: body.GetPosition().y, \
                      a: body.GetAngle()
        return @

    resetWorld: ->
        for id, entity of @entities
            @root.removeChild(entity.el)
            delete @entities[id]

        for id, body of @bodies
            @world.DestroyBody(body)
            delete @bodies[id]

        return @

    resetViewport: ->
        @root.style.fontSize = ""
        @root.style.right = ""
        @root.style.bottom = ""
        @root.style.left = ""

        return @

    applyImpulse: (id, degrees, power) ->
        vector = new b2Vec2(
            Math.cos(degrees * Math.PI / 180) * power,
            Math.sin(degrees * Math.PI / 180) * power
        )

        body = @bodies[id]
        body.ApplyImpulse(vector, body.GetWorldCenter())

        return @

    setViewportCenter: (x, y) ->
        scale = grepFloat(@root.style.fontSize) or 1.0

        # Calculate the default viewport position with the current scale.
        right = ((scale - 1) * @width * -0.05) / scale
        bottom = ((scale - 1) * @height * -0.05) / scale
        left = ((scale - 1) * @width * -0.05) / scale

        # Add the current transfer for the default viewport position.
        right = (@width / 2 - x) * -0.1 + right
        bottom = (@height / 2 - y) * 0.1 + bottom
        left = (@width / 2 - x) * 0.1 + left

        # Round up the values and update styles.
        @root.style.top = "#{Math.round(top * 1000) / 1000}em"
        @root.style.bottom = "#{Math.round(bottom * 1000) / 1000}em"
        @root.style.left = "#{Math.round(left * 1000) / 1000}em"

        return @

    setViewportScale: (scale) ->
        oldScale = grepFloat(@root.style.fontSize) or 1.0

        # Calculate the previous viewport scale.
        right = ((oldScale - 1) * @width * -0.05) / oldScale
        bottom = ((oldScale - 1) * @height * -0.05) / oldScale
        left = ((oldScale - 1) * @width * -0.05) / oldScale

        # Remove the transfer for the old scale.
        right = grepFloat(@root.style.right) - right
        bottom = grepFloat(@root.style.bottom) - bottom
        left = grepFloat(@root.style.left) - left

        # Add the transfer for the new scale.
        right = ((scale - 1) * @width * -0.05) / scale + right
        bottom = ((scale - 1) * @height * -0.05) / scale + bottom
        left = ((scale - 1) * @width * -0.05) / scale + left

        # Round up the values and update styles.
        @root.style.fontSize = "#{scale}em"
        @root.style.right = "#{Math.round(right * 1000) / 1000}em"
        @root.style.bottom = "#{Math.round(bottom * 1000) / 1000}em"
        @root.style.left = "#{Math.round(left * 1000) / 1000}em"

        return @

    pan: (from, to, seconds, callback, frame=0) ->
        factor = $.easing.swing(frame / (seconds * FPS))

        coords = @getViewportCenter()

        x = from.x + (to.x - from.x) * factor
        y = from.y + (to.y - from.y) * factor

        @setViewportCenter(x, y)
        if x != to.x or y != to.y then requestAnimFrame =>
            @pan(from, to, seconds, callback, frame + 1)
        else
            callback?()

    zoom: (from, to, seconds, callback, frame=0) ->
        factor = $.easing.swing(frame / (seconds * FPS))
        value = from + (to - from) * factor

        @setViewportScale(value)
        if factor < 1 then requestAnimFrame =>
            @zoom(from, to, seconds, callback, frame + 1)
        else
            callback?()

    animate: (callback) ->
        # Push the optional callback into callback pile.
        if typeof(callback) == 'function' then @callbacks.push(callback)

        # Prevent multiple simultenous animation loops.
        if @animating and callback != false then return @

        # Animate new step.
        @world.Step(1 / FPS, 10, 10) # time, velocity_iter, position_iter
        @world.ClearForces()

        # Update elements from bodies.
        body = @world.GetBodyList()
        while body
            id = body.GetUserData?()
            if id
                state = x: body.GetPosition().x, \
                        y: body.GetPosition().y, \
                        a: body.GetAngle() * -1  # -1 for the flipped y-axis
                @entities[id].update(state)
            body = body.GetNext()

        # The animation loop defaults to complete.
        done = true

        # Detect and destroy lost bodies (and see if anyone is left awake).
        body = @world.GetBodyList()
        while body
            id = body.GetUserData?()
            type = body.GetType?()
            if id and type != b2Body.b2_staticBody
                bbox = getBoundingBox(body)
                # if bbox.upperBound.x < 0 or bbox.upperBound.y < 0 \
                #         or bbox.lowerBound.x * SCALE > @width \
                #         or bbox.lowerBound.y * SCALE > @height
                if bbox.upperBound.y < 0 then @world.DestroyBody(body)
            # When awake body is found, we are not done yet
            if type != b2Body.b2_staticBody and body.IsAwake()
                done = false
            body = body.GetNext()

        if DEBUG then @world.DrawDebugData()

        # If we are done, execute all callbacks.
        if done
            tmp = []
            @animating = false
            while @callbacks.length > 0 then tmp.push @callbacks.shift()
            while tmp.length > 0 then tmp.shift()()
        # If we are not done yet, request a new animation frame.
        else
            @animating = true
            requestAnimFrame => @animate(false)

        return @


# The game.

jQuery ($) ->
    # Define the shared queue root
    $game = $('#game')

    # Define the game board background and foreground stages
    $board= $('#board')
    $tower = $('#tower')
    bg = new Stage $tower[0], $tower.width(), $tower.height()
    fg = new Stage $tower[0], $tower.width(), $tower.height()

    window.bg = bg  # for debugging...

    #
    # Build the dialer for entering the answer
    #

    $dialer = $('#dialer').css opacity: "0"
    dialer = new Stage $dialer[0], $dialer.width(), $dialer.height(), -10
    dialer.applyEntity(
        new StaticRectangle('dialer-floor', 0, 51,  dialer.width, 1))

    applyDialerCube = (idx) ->
        left = dialer.width / 2 - (60 * 9 / 2)

        dialCube= new Rectangle "dial-#{idx}", left + 60 * (idx - 1), 0, 50, 50
        dialCube.el.className += " color-#{idx}"
        dialer.applyEntity(dialCube)

        $dialCube = $(dialCube.el)
        $number = $("<span class=\"number number-#{idx}\">#{idx}</span>")
        $number.appendTo($dialCube)

        $dialCube.click ->
            dialer.applyImpulse("dial-#{idx}", 90, 40)
            dialer.animate()

            item = idx
            items = global.gameItems  # XXX: we rely on game globals here
            currentIdx = global.userItems.length  # XXX: the same

            if items[currentIdx] == item
                id = "fg-cube-#{currentIdx}"
                left = fg.width / 2 - 100 / 2
                cube = new Rectangle(id, left, fg.height, 100, 100)
                fg.applyEntity(cube)
                cube.el.className += " color-#{item}"
                $number = $("<span class=\"number\">#{item}</span>")
                $number.appendTo($(cube.el))

                $('body').append('<div class="modal-backdrop curtain"></div>')
                $game.queue -> fg.animate -> $game.dequeue()

                if currentIdx + 1 == items.length

                    bg.resetWorld()

                    $game.queue ->
                        $board.animate bottom: "0em", 1000
                        $dialer.animate bottom: "-7em", opacity: "0", 1000, ->
                            $game.dequeue()

                    $game.queue ->
                        fg.applyImpulse("fg-cube-0", -180, 15 * items.length)
                        fg.applyImpulse("fg-cube-1", -0, 20 * items.length)
                        fg.animate -> $game.dequeue()
                else
                    $game.queue ->
                        $("#bg-cube-#{currentIdx + 1}")
                            .addClass("placeholder").fadeIn 0, ->
                                $game.dequeue()

                $game.queue ->
                    $('.modal-backdrop.curtain').remove()
                    GameCheckUserPress(item)
                    $game.dequeue()

            else
                GameCheckUserPress(item)

    for idx in [1..9] then applyDialerCube(idx)

    # Define helpers for building the game. game is reseted for every
    # game.

    applyCube = (stage, id, position) ->
        left = stage.width / 2 - 100 / 2
        cube = new Rectangle(id, left, 0 + 120 * position, 100, 100)
        stage.applyEntity(cube)
        return cube

    queueAppend = ($cube, $el) ->
        $game.queue ->
            $el.appendTo($cube)
            $game.dequeue()
        return $game

    queueFadeOut = ($el) ->
        $game.queue ->
            $el.fadeOut 1000, -> $game.dequeue()
        return $game

    queueApplyImpulse = (stage, id, degrees, power) ->
        $game.queue ->
            stage.applyImpulse(id, degrees, power)
            $game.dequeue()
        return $game

    initGame = (data) ->
        $('body').append('<div class="modal-backdrop curtain"></div>')
        $('#level span').text data.level

        # "Reset"
        $board.css bottom: "0"
        $dialer.css bottom: "-6em", opacity: "0"
        bg.resetWorld().resetViewport().applyEntity(
            new StaticRectangle('bg-floor', -bg.width, -1, bg.width * 3, 1))
        fg.resetWorld().resetViewport().applyEntity(
            new StaticRectangle('fg-floor', -fg.width, -1, fg.width * 3, 1))

        # "Build the tower"
        for idx in [0...data.items.length]
            cube = applyCube(bg, "bg-cube-#{idx}", idx)
            cube.el.className += " color-#{data.items[idx]}"
        $game.queue -> bg.animate -> $game.dequeue()

        # "Countdown"
        for idx in [(data.items.length - 1)..0]
            $number = $("<span class=\"number\">#{data.items[idx]}</span>")
            queueAppend($("#bg-cube-#{idx}"), $number).delay(1000)
            queueFadeOut($("#bg-cube-#{idx}"))

        # Show the dialer
        $game.queue ->
            $board.animate bottom: "6em", 1000
            $("#bg-cube-0").addClass("placeholder").fadeIn 1000
            $dialer.animate opacity: "1", bottom: "0", 1000, -> $game.dequeue()

        $game.queue ->
            $('.modal-backdrop.curtain').remove()
            $game.dequeue()

    newGame = -> $.get('new', (data) ->
        GameInitialize(data.items, newGame: newGame)
        initGame(data)
    )

    runAnimation = -> 
        $('#animation').css('display', 'block')

        $someRight = 1000
        $('#b3').animate({left:'46px'}, $someRight)
        $('#b4').animate({left:'85px'}, $someRight)
        $('#harakka').animate({left:'47px'}, $someRight)

        $someLeft = 900
        $('#b3').animate({left:'30px'}, $someLeft)
        $('#b4').animate({left:'14px'}, $someLeft)
        $('#harakka').animate({left:'-37px'}, $someLeft)

        $someRight = 800
        $('#b3').animate({left:'46px'}, $someRight)
        $('#b4').animate({left:'85px'}, $someRight)
        $('#harakka').animate({left:'47px'}, $someRight)

        $someLeft = 700
        $('#b3').animate({left:'30px'}, $someLeft)
        $('#b4').animate({left:'14px'}, $someLeft)
        $('#harakka').animate({left:'-37px'}, $someLeft)

        $someRight = 600
        $('#b3').animate({left:'46px'}, $someRight)
        $('#b4').animate({left:'85px'}, $someRight)
        $('#harakka').animate({left:'47px'}, $someRight)

        $someLeft = 500
        $('#b3').animate({left:'30px'}, $someLeft)
        $('#b4').animate({left:'-14px'}, $someLeft)
        $('#harakka').animate({left:'-47px'}, $someLeft)

        $someLeft = 1000
        $('#b3').animate({left:'20px'}, $someLeft)
        $('#b4').animate({left:'-700px', top: '400px'}, $someLeft)
        $('#harakka').animate({left:'-337px', top: '800px'}, $someLeft)

        $('#b3,#b4,#harakka').promise().done( ->
            console.log('asdf')
            newGame()
        )

    $query = if location.search != undefined then location.search else ''
    newOrAnimGame = -> $.get('runanimation'+$query, (data) ->
        console.log('neoranim', data.animation)
        if data.animation
            runAnimation()
        else
            newGame()
    )

    # newGame()
    newOrAnimGame()
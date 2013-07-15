# -*- coding: utf-8 -*-
import datetime
import re


def get_view_method(obj, method_name, request):
    for adapter in request.registry.registeredAdapters():
        if len(adapter.required) > 2:
            if adapter.required[2].providedBy(obj):
                if adapter.name == method_name:
                    return adapter.factory.__view_attr__
    raise AttributeError("'{0:s}' not found".format(method_name))


def step_one_day(app, player_id):
    player = app.get_current_player(player_id)

    for day_str, daily_session in tuple(player.items()):
        for game_str, game_session in tuple(daily_session.items()):
            for dt_str, game_play in tuple(game_session.items()):
                game_play = game_play.copy()
                game_play["start"] = game_play["start"] - datetime.timedelta(1)

                dt = datetime.datetime(*map(int, re.findall("\d+", dt_str)))
                dt = dt - datetime.timedelta(1)

                del game_session[dt_str]
                game_session[str(dt)] = game_play

        day = datetime.datetime(*map(int, re.findall("\d+", day_str)))
        day = day - datetime.timedelta(1)
        player[day.strftime("%Y-%m-%d")] = player[day_str]
        del player[day_str]

    return player


def play_one_session(app, player_id, save_pass=False):
    app.request.cookies["active_player"] = player_id
    session = app.get_current_session(player_id)

    n = len(session.order)
    for i in range(n):
        next_game = app.get_next_game()
        assert session.order[0] == next_game

        game = app.games[next_game["game"]]
        method_name = get_view_method(game, "new", app.request)
        new_game = getattr(game, method_name)()

        items = new_game.get("items", new_game.get("sample", []))
        app.request.json_body = items

        if save_pass:
            game.save_pass()
        else:
            game.save_fail()

    assert len(session.order) == 0

    return app.get_current_player(player_id)

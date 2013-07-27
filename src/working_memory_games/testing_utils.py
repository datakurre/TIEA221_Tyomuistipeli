# -*- coding: utf-8 -*-
import datetime
import re
from pyramid.config.views import ViewDeriver


def get_view_attr_name(obj, method_name, request):

    #view_callable = request.registry.adapters.lookup(
    #    (IViewClassifier, implementedBy(IRequest), providedBy(obj)),
    #    IView, name=method_name, default=None)

    for adapter in request.registry.registeredAdapters():
        if len(adapter.required) > 2:
            if adapter.required[2].providedBy(obj):
                if adapter.name == method_name:
                    view_callable = adapter.factory
                    # A) Class based view method with xhr=True)
                    if hasattr(view_callable, "__view_attr__"):
                        return view_callable.__view_attr__
                    # B) Class based view method without xhr
                    elif hasattr(view_callable, "__wraps__"):
                        wrapped_view = view_callable.__wraps__
                        candidate = wrapped_view.func_closure[0].cell_contents
                        # Class based view method without cache-control
                        if type(candidate) == str:
                            return candidate
                        # Class based view method with cache-control
                        elif isinstance(candidate, ViewDeriver):
                            return candidate.kw["attr"]
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


def play_one_session(app, player_id, percentage=100, save_pass=[]):
    app.request.cookies["active_player"] = player_id
    session = app.get_current_session(player_id)

    n = int(len(session.order) * (percentage / 100.))
    if n - len(save_pass) > 0:
        save_pass += (n - len(save_pass)) * [False]

    for i in range(n):
        next_game = app.get_next_game()
        assert session.order[0] == next_game

        game = app.games[next_game["game"]]
        method_name = get_view_attr_name(game, "new", app.request)
        new_game = getattr(game, method_name)()

        items = new_game.get("items", new_game.get("sample", []))
        app.request.json_body = items

        if save_pass[i]:
            game.save_pass()
        else:
            game.save_fail()

    if percentage == 100:
        assert len(session.order) == 0

    return app.get_current_player(player_id)

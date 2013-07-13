# -*- coding: utf-8 -*-


def get_view_method(obj, method_name, request):
    for adapter in request.registry.registeredAdapters():
        if len(adapter.required) > 2:
            if adapter.required[2].providedBy(obj):
                if adapter.name == method_name:
                    return adapter.factory.__view_attr__
    raise AttributeError("'{0:s}' not found".format(method_name))


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

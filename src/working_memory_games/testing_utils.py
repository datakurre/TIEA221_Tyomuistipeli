# -*- coding: utf-8 -*-


def get_game_method(game, method_name, request):
    for adapter in request.registry.registeredAdapters():
        if len(adapter.required) > 2:
            if adapter.required[2].providedBy(game):
                if adapter.name == method_name:
                    return adapter.factory.__view_attr__

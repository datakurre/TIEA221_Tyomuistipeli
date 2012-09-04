# -*- coding: utf-8 -*-
"""ZCA interface definitions"""

from zope.interface import Interface


class IApplication(Interface):
    """Marker interface for the application root container"""


class IContainer(Interface):
    """Marker interface for container object"""

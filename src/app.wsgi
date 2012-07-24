# -*- coding: utf-8
import sys, os,	os.path
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__))) 
os.chdir(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]) 

from app import *

import bottle


application = bottle.default_app()


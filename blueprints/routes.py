"""
Blueprints routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from blueprints.views import Blueprint

routes = (
    ('GET', '/spawner/blueprints', Blueprint),
)

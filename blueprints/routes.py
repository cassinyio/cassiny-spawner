"""
Blueprints routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from blueprints.views import Blueprint

routes = (
    ('*', '/spawner/blueprints', Blueprint),
    ('POST', '/spawner/blueprints/{cargo_id}', Blueprint),
)

"""
Blueprints routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from blueprints.views import Blueprint

routes = (
    ('*', '/api/spawner/blueprints', Blueprint),
    ('POST', '/api/spawner/blueprints/cargo/{cargo_id}', Blueprint),
)

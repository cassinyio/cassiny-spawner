"""
APIs routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from apis.views import APIs

routes = (
    ('GET', '/api/spawner/apis', APIs),
    ('POST', '/api/spawner/apis', APIs),
    ('PATCH', '/api/spawner/apis/{api_id}', APIs),
    ('DELETE', '/api/spawner/apis/{api_id}', APIs),
)

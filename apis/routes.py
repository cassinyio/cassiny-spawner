"""
APIs routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from apis.views import APIs, Logs

routes = (
    ('GET', '/api/spawner/apis', APIs),
    ('POST', '/api/spawner/apis', APIs),
    ('PATCH', '/api/spawner/apis/{api_ref}', APIs),
    ('DELETE', '/api/spawner/apis/{api_ref}', APIs),
    ('GET', '/api/spawner/apis/logs/{api_ref}', Logs),
)

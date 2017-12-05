"""
APIs routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from apis.views import APIs

routes = (
    ('GET', '/spawner/apis', APIs),
    ('POST', '/spawner/apis', APIs),
    ('PATCH', '/spawner/apis/{api_id}', APIs),
    ('DELETE', '/spawner/apis/{api_id}', APIs),
)

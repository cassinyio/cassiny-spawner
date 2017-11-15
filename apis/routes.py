"""
APIs routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from apis.views import APIs

routes = (
    ('GET', '/v1/apis', APIs),
    ('POST', '/v1/apis', APIs),
    ('PATCH', '/v1/apis/{api_id}', APIs),
    ('DELETE', '/v1/apis/{api_id}', APIs),
)

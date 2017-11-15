"""
Cargos routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from cargos.views import Cargo

routes = (
    ('GET', '/v1/cargos', Cargo),
    ('POST', '/v1/cargos', Cargo),
    ('DELETE', '/v1/cargos/{cargo_id}', Cargo),
)

"""
Cargos routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from cargos.views import Cargo

routes = (
    ('GET', '/api/spawner/cargos/{cargo_ref}', Cargo),
    ('GET', '/api/spawner/cargos', Cargo),
    ('POST', '/api/spawner/cargos', Cargo),
    ('DELETE', '/api/spawner/cargos/{cargo_ref}', Cargo),
)

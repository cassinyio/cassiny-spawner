"""
Cargos routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from cargos.views import Cargo

routes = (
    ('GET', '/spawner/cargos/{cargo_id}', Cargo),
    ('GET', '/spawner/cargos', Cargo),
    ('POST', '/spawner/cargos', Cargo),
    ('DELETE', '/spawner/cargos/{cargo_id}', Cargo),
)

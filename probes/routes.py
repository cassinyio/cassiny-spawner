"""
Probes routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from probes.views import Probe

routes = (
    ('GET', '/spawner/probes', Probe),
    ('GET', '/spawner/probes/{probe_id}', Probe),
    ('POST', '/spawner/probes', Probe),
    ('PATCH', '/spawner/probes/{probe_id}', Probe),
    ('DELETE', '/spawner/probes/{probe_id}', Probe),
)

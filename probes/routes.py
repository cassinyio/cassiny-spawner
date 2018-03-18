"""
Probes routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from probes.views import Logs, Probe

routes = (
    ('GET', '/api/spawner/probes', Probe),
    ('GET', '/api/spawner/probes/{probe_ref}', Probe),
    ('POST', '/api/spawner/probes', Probe),
    ('PATCH', '/api/spawner/probes/{probe_ref}', Probe),
    ('DELETE', '/api/spawner/probes/{probe_ref}', Probe),
    ('GET', '/api/spawner/probes/logs/{probe_ref}', Logs),
)

"""
Probes routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from probes.views import Probe

routes = (
    ('GET', '/v1/probes', Probe),
    ('POST', '/v1/probes', Probe),
    ('PATCH', '/v1/probes/{probe_id}', Probe),
    ('DELETE', '/v1/probes/{probe_id}', Probe),
)

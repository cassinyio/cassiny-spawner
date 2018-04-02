"""
Monitoring routes.

Copyright (c) 2017, Cassiny.io OÜ
All rights reserved.
"""

from monitoring.views import Events

routes = (
    ('GET', '/api/spawner/events', Events),
)

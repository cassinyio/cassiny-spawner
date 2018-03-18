"""
Events routes.

Copyright (c) 2017, Cassiny.io OÜ
All rights reserved.
"""

from events.views import Events, Logs

routes = (
    # Events
    ('*', '/api/spawner/events', Events),
    ('GET', '/api/spawner/logs/{service_id}', Logs),
)

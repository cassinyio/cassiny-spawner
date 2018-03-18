"""
Events routes.

Copyright (c) 2017, Cassiny.io OÜ
All rights reserved.
"""

from events.views import Events

routes = (
    # Events
    ('*', '/api/spawner/events', Events),
)

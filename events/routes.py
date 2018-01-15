"""
Events routes.

Copyright (c) 2017, Cassiny.io OÜ
All rights reserved.
"""

from events.views import Events, Logs

routes = (
    # Auth
    ('*', '/events', Events),
    ('*', '/logs/{service-id}', Logs),

)

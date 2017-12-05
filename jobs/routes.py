"""
Jobs routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from jobs.views import Jobs

routes = (
    ('GET', '/spawner/jobs', Jobs),
    ('POST', '/spawner/jobs', Jobs),
    ('PATCH', '/spawner/jobs/{job_id}', Jobs),
    ('DELETE', '/spawner/jobs/{job_id}', Jobs),
)

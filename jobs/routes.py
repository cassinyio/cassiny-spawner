"""
Jobs routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from jobs.views import Jobs

routes = (
    ('GET', '/api/spawner/jobs', Jobs),
    ('POST', '/api/spawner/jobs', Jobs),
    ('PATCH', '/api/spawner/jobs/{job_ref}', Jobs),
    ('DELETE', '/api/spawner/jobs/{job_ref}', Jobs),
)

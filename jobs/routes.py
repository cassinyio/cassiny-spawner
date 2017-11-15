"""
Jobs routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from jobs.views import Jobs

routes = (
    ('GET', '/v1/jobs', Jobs),
    ('POST', '/v1/jobs', Jobs),
    ('PATCH', '/v1/jobs/{job_id}', Jobs),
    ('DELETE', '/v1/jobs/{job_id}', Jobs),
)

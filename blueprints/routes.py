"""
Blueprints routes.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from blueprints.views import (
    Blueprint,
    BlueprintFromFolder,
    BuildFromS3,
)

routes = (
    ('*', '/api/spawner/blueprints', Blueprint),
    ('DELETE', '/api/spawner/blueprints/{blueprint_ref}', Blueprint),
    ('POST', '/api/spawner/blueprints/create_from_cargo', BuildFromS3),
    ('POST', '/api/spawner/blueprints/create_from_folder', BlueprintFromFolder),
)

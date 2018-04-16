
"""
Jobs helpers.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


from rampante import streaming

from spawner import Spawner


async def delete_a_job(job_uuid: str, job_name: str, user_id: str) -> None:
    await Spawner.job.delete(name=job_name)

    event = {
        "uuid": job_uuid,
        "user_id": user_id,
        "name": job_name,
    }
    await streaming.publish("service.job.deleted", event)

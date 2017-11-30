"""
remote_api.py
~~~~~~~~~
Remote API to control cargo servers

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging

import asyncssh

log = logging.getLogger(__name__)


async def run_ssh(remote_host: str, command: str):
    """
    Run ssh command.

    remote_host: server with cargos
    command: remote command that you want to run
    """
    try:
        async with asyncssh.connect(remote_host) as conn:
            result = await conn.run(command, check=True)
    except (OSError, asyncssh.Error):
        log.exception(f'Failed to run command {command} on {remote_host}')
        result = False
    return result


async def create_cargo(remote_host: str, cargo_id: str):
    """
    Create a cargo inside the remote_host.

    remote_host: machine where the cargo is based
    user: owner of the cargo
    """
    # we create the fs as a normal user
    # to keep the same owner, otherwise it would be root
    command = (f"zfs create spacedock/{cargo_id} && "
               f"sudo zfs mount spacedock/{cargo_id}")
    result = await run_ssh(remote_host, command)
    return result


async def destroy_cargo(remote_host: str, cargo_id: str):
    """
    Destroy the cargo.

    remote_host: machine where the cargo is based
    user: owner of the cargo
    """
    command = f"sudo zfs destroy spacedock/{cargo_id}"
    result = await run_ssh(remote_host, command)
    return result


async def set_quota(remote_host: str, cargo_id: str, quota: int):
    """
    Set a max size for the cargo.

    remote_host: machine where the cargo is based
    user: owner of the cargo
    quota: quote for the cargo, in GB
    """
    command = f"zfs set quota={quota}G spacedock/{cargo_id}"
    result = await run_ssh(remote_host, command)
    return result


async def get_space(remote_host: str, cargo_id: str):
    """
    Get the current size of the cargo.

    remote_host: machine where the cargo is based
    user: owner of the cargo
    """
    command = f"zfs list spacedock/{cargo_id}"
    result = await run_ssh(remote_host, command)
    if result:
        stdout = result.stdout
        keys, values = [elements.split() for elements in stdout.splitlines()]
        return {k.lower(): v for k, v in zip(keys, values)}
    return result

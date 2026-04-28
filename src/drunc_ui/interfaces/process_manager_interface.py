"""Module providing functions to interact with the drunc process manager."""

from collections.abc import Iterable
from enum import Enum

from django.conf import settings
from drunc.process_manager.process_manager_driver import ProcessManagerDriver
from drunc.utils.grpc_utils import ServerUnreachable
from druncschema.process_manager_pb2 import (
    LogRequest,
    ProcessInstanceList,
    ProcessQuery,
    ProcessUUID,
)
from druncschema.token_pb2 import Token


def get_process_manager_driver(username: str) -> ProcessManagerDriver:
    """Get a ProcessManagerDriver instance."""
    token = Token(token=f"{username}-token", user_name=username)
    return ProcessManagerDriver(settings.PROCESS_MANAGER_URL, token=token)


def get_session_info(username: str) -> ProcessInstanceList:
    """Get info about all sessions from process manager."""
    pmd = get_process_manager_driver(username)
    query = ProcessQuery(names=[".*"])
    try:
        return pmd.ps(query)
    except ServerUnreachable as e:
        raise ServerUnreachable("Unable to connect with the Process Manager") from e


class ProcessAction(Enum):
    """Enum for process actions."""

    RESTART = "restart"
    KILL = "kill"
    FLUSH = "flush"


def process_call(uuids: Iterable[str], action: ProcessAction, username: str) -> ProcessInstanceList:
    """Perform an action on a process with a given UUID.

    Args:
        uuids: List of UUIDs of the process to be actioned.
        action: Action to be performed {restart,flush,kill}.
        username: Username of the user performing the action
    """
    pmd = get_process_manager_driver(username)
    uuids_ = [ProcessUUID(uuid=u) for u in uuids]
    query = ProcessQuery(uuids=uuids_)

    try:
        match action:
            case ProcessAction.RESTART:
                return pmd.restart(query)
            case ProcessAction.KILL:
                return pmd.kill(query)
            case ProcessAction.FLUSH:
                return pmd.flush(query)
            case _:
                raise ValueError(f"Unknown action: {action}")
    except ServerUnreachable as e:
        raise ServerUnreachable("Unable to connect with the Process Manager") from e


def get_process_logs(uuid: str, username: str) -> list[str]:
    """Retrieve logs for a process from the process manager.

    Args:
      uuid: UUID of the process.
      username: Username of the user requesting the logs

    Returns:
      The process logs, as a list of lines.
    """
    pmd = get_process_manager_driver(username)
    query = ProcessQuery(uuids=[ProcessUUID(uuid=uuid)])
    request = LogRequest(query=query, how_far=100)
    response = pmd.logs(request)
    return list(response.lines)


def boot_process(user: str, session_name: str, n_processes: int, sleep: int, n_sleeps: int) -> None:
    """Boot a process with the given data.

    Args:
        user: the user to boot the process as.
        session_name: the name of the session.
        n_processes: the number of processes to boot.
        sleep: the sleep duration.
        n_sleeps: the number of sleeps.
    """
    pmd = get_process_manager_driver(user)
    pmd.dummy_boot("root", session_name, n_processes, sleep, n_sleeps)


def get_hostnames(user: str) -> dict[str, str]:
    """Get the hostnames of the processes for the given user.

    Args:
        user: The user to get the hostnames for.

    Returns:
        The hostnames of the processes for the given user.
    """
    session_info = get_session_info(user)
    hostnames = {}
    for process_instance in session_info.values:
        hostnames[process_instance.process_description.metadata.name] = (
            process_instance.process_description.metadata.hostname
        )
    return hostnames

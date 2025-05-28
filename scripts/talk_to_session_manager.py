"""Example script used to check communication with the session manager.

This is intended to be run within docker from the `app` service, i.e.:

```
docker compose exec app python scripts/talk_to_session_manager.py
```

and provides a basic proof of principle of communicating with the session manager via
gRPC.

The script starts a dummy session on the session manager and then retrieves the details
of all sessions and prints them to stdout.
"""

from drunc.session_manager.session_manager_driver import SessionManagerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname

if __name__ == "__main__":
    # connect to and query the root controller
    token = create_dummy_token_from_uname()
    sm = SessionManagerDriver("drunc_sm:50000", token=token)
    session = sm.list_all_sessions().data
    print("Sessions: ", session)
    configs = sm.list_all_configs().data
    print("Configs: ", configs)

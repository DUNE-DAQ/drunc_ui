"""Example script used to check communication with the controller.

This is intended to be run within docker from the `app` service, i.e.:

```
docker compose exec app python scripts/talk_to_controller.py
```

and provides a basic proof of principle of communicating with the controller via
gRPC.
"""

from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname

if __name__ == "__main__":
    token = create_dummy_token_from_uname()
    controller = ControllerDriver("localhost:3333", token=token, aio_channel=True)

    val = controller.get_status()
    print(val)

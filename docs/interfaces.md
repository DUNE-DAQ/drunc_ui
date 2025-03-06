# Interfaces

The `interfaces` package includes the functionality that connects the UI to the `drunc`
backend. Its functionality is used to extract all the system information displayed by
the various Django apps and to action changes in the backend due to the users
interaction.

It is made of the following components:

- `controller_interface`: Interacts with the `drunc` controller, running applications
and driving changes in the finite state machine (FSM). See the page for the
[controller](./controller.md) for more information.
- `process_manager_interface`: Interacts with the `drunc` process manager, starting,
killing and monitoring the processes running in the system. See the page for the
[process manager](./process_manager.md) for more information.
- `session_manager_interface`: Interacts with the `drunc` session manager, starting new
sessions and transferring them to new users. See the page for the
[session manager](./session_manager.md) for more information.

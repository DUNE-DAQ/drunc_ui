"""Module that implements `drunc` finite state machine."""

from typing import Any

from statemachine import State, StateMachine

from . import controller_interface as ci


class DruncFSM(StateMachine):
    """Finite state machine for the `drunc` controller."""

    # The states the controller can be in
    none = State("None", initial=True)
    initial = State("Initial")
    configured = State("Configured")
    ready = State("Ready")
    running = State("Running")
    dataflow_drained = State("Dataflow_Drained")
    triggered_sources_stopped = State("Triggered_Sources_Stopped")

    # The transitions between the states
    boot = none.to(initial)
    terminate = initial.to(none)
    conf = initial.to(configured)
    scrap = configured.to(initial)
    start = configured.to(ready)
    enable_triggers = ready.to(running)
    disable_triggers = running.to(ready)
    drained_dataflow = ready.to(dataflow_drained)
    stop_triggered_sources = dataflow_drained.to(triggered_sources_stopped)
    stop = triggered_sources_stopped.to(configured)

    @classmethod
    def get(cls, state: str | None = None) -> "DruncFSM":
        """Get a DruncFSM object matching the Controller current state.

        TODO: Remove input argument and use the current state from the controller once
        the controller is implemented

        Args:
            state (str, optional): The state to start the FSM in. Defaults to None.

        Returns:
            DruncFSM: The matching DruncFSM object.
        """
        if state:
            return cls(start_value=state.lower())
        return cls(start_value=ci.get_fsm_state().lower())

    def to_dict(self) -> dict[str, list[dict[str, str]]]:
        """Return the FSM states and events as a dictionary.

        The states will be the keys and the valid events for each state a list of
        values.

        Returns:
            dict[str, list[str]]: The states and events as a dictionary.
        """
        states = {
            state.name: [
                {"event": transition.event, "target": transition.target.name}
                for transition in state.transitions
            ]
            for state in self.states
        }
        return {state: states[state] for state in self.ordered_states}

    @property
    def ordered_states(self) -> list[str]:
        """Return the order of the states for the visual representation.

        Returns:
            list[str]: The order of the states.
        """
        return [
            "None",
            "Initial",
            "Configured",
            "Ready",
            "Running",
            "Dataflow_Drained",
            "Triggered_Sources_Stopped",
        ]

    def send(self, event: str, **kwargs: dict[str, Any]) -> None:  # type: ignore[misc]
        """Send an event to the FSM.

        This method sends the event to the FSM and only if the response is
        successful, the state of this object will change to the one reported by the
        controller. In practice, this offloads the state change to the controller,
        avoiding any inconsistencies.

        Args:
            event (str): The event to send.
            **kwargs (dict[str, Any]): The arguments for the event.
        """
        super().send(event, **kwargs)

        # TODO: Remove above and uncomment below once the controller is implemented
        # if event not in [t.event for t in self.current_state.transitions]:
        #     raise ValueError(
        #         f"Event '{event}' is not a valid transition for "
        #         f" {self.current_state.name}."
        #     )

        # result = ci.send_event(event, **kwargs)
        # if result.value == 0:
        #     self.current_state_value = ci.get_fsm_state()
        # else:
        #     raise ValueError(f"Event '{event}' failed with flag {result.name}.")

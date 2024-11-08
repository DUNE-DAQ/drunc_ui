"""Module that implements `drunc` finite state machine."""

from statemachine import State, StateMachine

from .controller_interface import get_fsm_state, send_event


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
    def get(cls) -> "DruncFSM":
        """Get a DruncFSM object matching the Controller current state.

        Returns:
            DruncFSM: The matching DruncFSM object.
        """
        return cls(start_value=get_fsm_state())

    def send(self, event: str, **kwargs: dict[str, str]) -> None:
        """Send an event to the FSM.

        This method sends the event to the FSM and only if the response is
        successful, the state of this object will change to the one reported by the
        controller. In practice, this offloads the state change to the controller,
        avoiding any inconsistencies.

        Args:
            event (str): The event to send.
            **kwargs (dict[str, str]): The arguments for the event.
        """
        if event not in [t.event for t in self.current_state.transitions]:
            raise ValueError(
                f"Event '{event}' is not a valid transition for "
                f" {self.current_state.name}."
            )

        result = send_event(event, **kwargs)
        if result.value == 0:
            self.current_state_value = get_fsm_state()
        else:
            raise ValueError(f"Event '{event}' failed with flag {result.name}.")

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
        """Return the order of the states.

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

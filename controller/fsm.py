"""Module that implements `drunc` finite state machine."""

from statemachine import State, StateMachine

from .controller_interface import get_fsm_state


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

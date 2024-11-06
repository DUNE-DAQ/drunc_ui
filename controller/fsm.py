"""Module that implements `drunc` finite state machine."""

from statemachine import State, StateMachine


class DruncFSM(StateMachine):
    """Finite state machine for the `drunc` controller."""

    # The states the controller can be in
    none = State("None", initial=True)
    initial = State("Initial")
    configured = State("Configured")
    ready = State("Ready")
    running = State("Running")
    triggered_sources_stopped = State("TriggeredSourcesStopped")
    dataflow_drained = State("DataflowDrained")

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

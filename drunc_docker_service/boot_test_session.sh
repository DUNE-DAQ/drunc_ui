#!/bin/bash

# boot full test session
if [[ "$CSC_SESSION" == "lr-session" ]]; then
    CONFIG="config/lrSession.data.xml"
    SESSION=$CSC_SESSION
else
    CONFIG="config/daqsystemtest/example-configs.data.xml"
    SESSION="local-2x3-config"
fi

/entrypoint.sh drunc-process-manager-shell grpc://localhost:10054 boot $CONFIG $SESSION

#!/bin/bash

# setup dunedaq environment
. /basedir/NFD_DEV_241114_A9/env.sh

# boot full test session
drunc-process-manager-shell grpc://localhost:10054 boot config/daqsystemtest/example-configs.data.xml local-2x3-config

#!/bin/bash

# setup dunedaq environment
. /basedir/"$NIGHTLY_TAG"/env.sh

exec "$@"

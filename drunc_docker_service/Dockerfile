FROM ghcr.io/imperialcollegelondon/dunedaq_dev_environment:nightly-241114

RUN yum install -y openssh-server && yum clean all

# required for dunedaq setup
SHELL ["/bin/bash", "-c"]

WORKDIR /basedir

# setup for the the dune development environment that provides the full set of
# dependencies required for booting of the controller test session
# See https://github.com/DUNE-DAQ/drunc/wiki/Setup-drunc-with-DUNE-DAQ for explanation
RUN source /cvmfs/dunedaq.opensciencegrid.org/setup_dunedaq.sh && \
        setup_dbt latest_v5 && \
        dbt-create -n NFD_DEV_241114_A9 && \
        cd NFD_DEV_241114_A9 && \
        source env.sh && \
        dbt-build && \
        dbt-workarea-env
WORKDIR /basedir/NFD_DEV_241114_A9/

COPY process-manager-kafka.json /

# setup ssh server config and keys
ADD ssh-setup.sh /
RUN bash /ssh-setup.sh

RUN mkdir -p /usr/src/app
ADD entrypoint.sh /
RUN chmod a+x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

ADD wibeth_output_all_zeros.bin /cvmfs/dunedaq.opensciencegrid.org/assets/files/d/d/1/wibeth_output_all_zeros.bin

ADD boot_test_session.sh /
RUN chmod a+x /boot_test_session.sh

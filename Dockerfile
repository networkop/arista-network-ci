FROM docker:stable-dind

RUN apk update && \
    apk add python3-dev && \
    apk add git && \
    apk add python2-dev && \
    apk add py2-setuptools && \
    apk add py-pip && \
    apk add ansible && \
    python2 -m easy_install pip


# Ansible and docker-topo dependencies
RUN python3 -m pip install netaddr
RUN python3 -m pip install jmespath
RUN python2 -m pip install jmespath

# This bit installs docker-topo
RUN python3 -m pip install git+https://github.com/networkop/arista-ceos-topo.git

# This bit installs Arista Network validation
#COPY network_validation-1.0.1.tar.gz /tmp
#RUN python2 -m pip install /tmp/network_validation-1.0.1.tar.gz

# This bit installs pybatfish and its dependencies
RUN apk add --virtual .build-deps g++
RUN apk add libstdc++
RUN python3 -m pip install git+https://github.com/batfish/pybatfish.git@1jan2019
RUN apk del .build-deps



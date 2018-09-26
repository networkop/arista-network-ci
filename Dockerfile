FROM docker:stable-dind

RUN apk update && \
    apk add python3-dev && \
    apk add git && \
    apk add python2-dev && \
    apk add py-pip && \
    apk add ansible

# Ansible and docker-topo dependencies
RUN pip3 install netaddr
RUN pip3 install jmespath
RUN pip2 install jmespath

# This bit installs docker-topo
RUN pip3 install git+https://github.com/networkop/arista-ceos-topo.git

# This bit installs Arista Network validation
COPY network_validation-1.0.1.tar.gz /tmp
RUN pip2 install /tmp/network_validation-1.0.1.tar.gz

# This bit installs pybatfish and its dependencies
RUN apk add --virtual .build-deps g++
RUN apk add libstdc++
RUN pip3 install git+https://github.com/batfish/pybatfish.git
RUN apk del .build-deps



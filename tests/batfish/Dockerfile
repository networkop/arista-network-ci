FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    git lsb-release wget unzip \
    openjdk-8-jdk-headless maven binutils libgomp1

RUN git clone --depth 1 --branch 21sep2018 https://github.com/batfish/batfish.git

RUN ["/bin/bash", "-c", "cd batfish && \
                         tools/install_z3.sh && \
                         source tools/batfish_functions.sh && \
                         batfish_build_all"]

CMD ["/bin/bash", "-c", "cd batfish && \
                         source tools/batfish_functions.sh && \
                         allinone -runclient false -coordinatorargs \"-templatedirs ./questions\""]

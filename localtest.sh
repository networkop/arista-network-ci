docker build -t networkci .
docker tag networkci 172.16.0.46:5000/networkci
docker push 172.16.0.46:5000/networkci

docker run -it -v $(pwd):/home --privileged --name networkci networkci sh

export PRIMARY_IP=172.16.0.46
export LOCAL_REGISTRY=$PRIMARY_IP:5000
export CONF_DIR=./build/configs
dockerd --insecure-registry $LOCAL_REGISTRY &
docker image pull $LOCAL_REGISTRY/ceos:4.20.0F
docker image pull networkop/alpine-host:latest
docker image tag networkop/alpine-host alpine-host


cp  ./build/configs/prod_* ./tests/batfish/configs/
./tests/batfish/leaf-3.py ./tests/batfish/

docker-topo --create topo/topo.yml 
docker exec clos_Leaf-3 wfw Aaa


cd ./tests/robot
mkdir ./report
validate_network.py --config test.yml --reportdir report


## Playbook

Build "current" configs for production network (missing Leaf-3 BGP peerings)

cd build
ansible-playbook -e @group_vars/current.yml -e buildenv=prod ./build.yml
cp -r ./configs ../prod/

cd ../
cp  ./prod/configs/prod_* ./tests/batfish/configs/
./tests/batfish/leaf-3.py ./tests/batfish/

cd prod
~/arista-ceos-topo/bin/docker-topo --create topo.yml


cd ../build
ansible-playbook --diff --check diff.yml

ansible-playbook -e PROD_IP=localhost -e buildenv push.yml

~/arista-ceos-topo/bin/docker-topo --destroy topo.yml

ansible-playbook -e @group_vars/indended.yml -e buildenv=prod ./build.yml


docker build -t batfish tests/batfish/
docker run -d --name batfish -p 9996:9996 -p 9997:9997 -p 9998:9998 batfish 

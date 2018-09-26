*** Settings ***
Documentation     Leaf-3 | Data Plane Testing
Suite Setup       Connect To Switches
Suite Teardown    Clear All Connections
Library           AristaLibrary
Library           AristaLibrary.Expect
Library           Collections
Library           Process


*** Variables ***
${LEAF1_SVI}    192.168.10.1
${LEAF2_SVI}    192.168.20.1
${HOST1}    192.168.10.10
${HOST2}    192.168.20.20

*** Test Cases ***
Remote leaves reachability | Leaf1
    [Documentation]    Leaf1's SVIs Ping loss  < 100%
    ${leaf1}    Address Is reachable    ${LEAF1_SVI}
    Should be True  ${leaf1}

Remote leaves reachability | Leaf2
    [Documentation]    Leaf2's SVIs Ping loss < 100%
    ${leaf2}    Address Is reachable    ${LEAF2_SVI}
    Should be True  ${leaf2}

E2E connectivity
    [Documentation]    Check if Host-3 can reach other hosts
    ${host1}=    Run Process    docker exec -i lab_Host-3 sudo ping -c 3 ${HOST1}     shell=yes
    ${host2}=    Run Process    docker exec -i lab_Host-3 sudo ping -c 3 ${HOST2}     shell=yes
    Should Be Equal As Integers    ${host1.rc}    0
    Should Be Equal As Integers    ${host2.rc}    0

*** Keywords ***
Connect To Switches
    [Documentation]    Establish connection to a switch which gets used by test cases.
    Connect To    host=${Leaf-3_HOST}    transport=${TRANSPORT}    username=${USERNAME}    password=${PASSWORD}    port=${Leaf-3_PORT}

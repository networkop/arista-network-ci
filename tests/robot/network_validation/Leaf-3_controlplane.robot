*** Settings ***
Documentation     Leaf-3 | Control Plane Testing
Suite Setup       Connect To Switches
Suite Teardown    Clear All Connections
Library           AristaLibrary
Library           AristaLibrary.Expect
Library           Collections


*** Variables ***
${LEAF1_LOOPBACK}    1.1.1.1/32
${LEAF2_LOOPBACK}    1.1.1.2/32

*** Test Cases ***
BGP Session
    [Documentation]    Check if BGP peerings are Established
    ${bgp}=     Get Command Output    cmd=show ip bgp summary
    ${result}=    Get Dictionary Items    ${bgp}
    ${vrfs}=    Get From Dictionary    ${result[1]}    vrfs
    ${default_vrf}=     Get From Dictionary    ${vrfs}    default
    ${peers}=   Get From Dictionary     ${default_vrf}     peers
    :FOR    ${peer}     IN      @{peers}
    \   Log     ${peer}
    \   ${peer_dict}=   Get From Dictionary     ${peers}     ${peer}
    \   ${state}=   Get From Dictionary     ${peer_dict}     peerState
    \   Should Be Equal     ${state}    Established

BGP Updates
    [Documentation]    Check if loopbacks are known via BGP
    Get Command Output    cmd=show ip bgp
    Expect    vrfs default bgpRouteEntries    to contain    ${LEAF1_LOOPBACK}
    Expect    vrfs default bgpRouteEntries    to contain   ${LEAF2_LOOPBACK}

Control Plane Snapshot
    [Documentation]    Capture the current state of BGP RIB
    ${bgp_state}=   Get Command Output  cmd=show ip bgp
    Log     ${bgp_state}

*** Keywords ***
Connect To Switches
    [Documentation]    Establish connection to a switch which gets used by test cases.
    Connect To    host=${Leaf-3_HOST}    transport=${TRANSPORT}    username=${USERNAME}    password=${PASSWORD}    port=${Leaf-3_PORT}

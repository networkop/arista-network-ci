#!/usr/bin/env python3
import sys
import logging
import argparse
from pybatfish.client.commands import *
from pybatfish.question.question import load_questions, list_questions
from pybatfish.question import bfq
from pybatfish.datamodel.flow import HeaderConstraints as header


def test_dataplane(isFailed, fromNode, checkMultipath=True):
    ips = bfq.ipOwners().answer().frame()
    loopbacks = ips[(ips['Interface'] == 'Loopback0') & (ips['Active'])]

    localIP = loopbacks[loopbacks['Node'] == fromNode]['IP'][0]
    leaves = set(loopbacks[loopbacks['Node'].str.contains('leaf')]['IP'])
    leaves.remove(localIP)
    spines = set(loopbacks[loopbacks['Node'].str.contains('spine')]['IP'])
    mpath = len(spines)

    logging.info("Progress: Analyzing traceroute from Leaf-3 to Leaf-1 and Leaf-2")
    # Set up the resulting data structure
    troute = dict()
    for leaf in leaves:
        troute[leaf] = dict()

    # Build headers for traceroute flows
    for leaf in leaves:
        troute[leaf]['header'] = header(srcIps=localIP,dstIps=leaf)

    # Ask questions about traceroute
    for leaf,data in troute.items():
        troute[leaf]['trace'] = bfq.traceroute(startLocation=fromNode, headers=data['header']).answer()
    
    # Get first flow disposition for traces
    for leaf,data in troute.items():
        troute[leaf]['result'] = data['trace'].get('answerElements')[0]['rows'][0]['Traces'][0]['disposition']

    # Get traceroute paths to reach Leaf-1 and  Leaf-2
    for leaf,data in troute.items():
        troute[leaf]['paths'] = data['trace'].get('answerElements')[0]['rows'][0]['Traces']

    # Get traceroute hops to reach Leaf-1 and Leaf-2
    for leaf,data in troute.items():
        troute[leaf]['hops'] = data['trace'].get('answerElements')[0]['rows'][0]['Traces'][0].get('hops',[])

    # Now let's check that the traceroute behaves as we expect
    for leaf, data in troute.items():
        if data['result'] != 'ACCEPTED':
            logging.error("Traceroute to {} has failed: {}".format(leaf, data['result']))
            isFailed = True
        else:
            logging.info("Traceroute Progress: {}".format(data['result']))
        # Number of paths should be equal to the number of spines
        if len(data['paths']) != mpath:
            logging.error("Number of paths {} != {} number of spines".format(len(data['paths']), mpath))
            logging.error(data['paths'])
            isFailed = True
        else:
            logging.info("Number of paths {} == {} number of spines".format(len(data['paths']), mpath))
        # Traceroute has to traverse exactly two hops
        for path in data['paths']:
            if len(path.get('hops',[])) != 2:
                logging.error("Traceroute has not traversed exactly two hops")
                logging.error(path)
                isFailed = True 
            else:
                logging.info("Traceroute traversed exactly two hops")
    
    return isFailed

def test_controlplane(isFailed):
    # Define a list of Spine switches
    spines = set(bfq.nodeProperties(nodes='spine.*').answer().frame()['Node'])
    logging.info("Progress: Analyzing control plane properties")

    # Get all BGP session status for leaf nodes
    bgp = bfq.bgpSessionStatus(nodes='leaf.*').answer().frame()
    
    # All leaves should have at least one peering with each spine
    violators = bgp.groupby('Node').filter(lambda x: set(x['Remote_Node']).difference(spines) != set([]))
    if len(violators) > 0:
        logging.error("Found leaves that do not have at least one peering to each spine")
        logging.error(violators[['Node', 'Remote_Node']])
        isFailed = True
    else:
        logging.info("All leaves have at least one peering with each spine")
   
    # All leaves should only peer with spines
    non_spines = bgp[~bgp['Remote_Node'].str.contains('spine', na=False)]
    if len(non_spines) > 0:
        logging.error("Leaves do not only peer with spines")
        logging.error(non_spines[['Node', 'Remote_Node']])
        isFailed = True
    else:
        logging.info("Leaves only peer with spines")

    return isFailed

def test_config_sanity(isFailed):
    logging.info("Progress: Searching for unused and undefined data structures")
    # Find all undefined data structures
    undefined = bfq.undefinedReferences().answer().frame()
    if len(undefined) >  0:
        logging.error("Found undefined data structures")
        logging.error(undefined)
        isFailed = True
    else:
        logging.info("No undefined data structures found")

    # Find all unused data structures
    unused = bfq.unusedStructures().answer().frame()
    if len(unused) >  0:
        logging.error("Found unused data structures")
        logging.error(unused)
        isFailed = True
    else:
        logging.info("No unused data structures found")

    return isFailed

def print_reduced_rechability(answer):
    logging.info("Progress: the following flows will fail as the result of an outage")
    for row in answer['rows']:
        logging.info("{} -> {}".format(row['flow']['srcIp'], row['flow']['dstIp']))


def main():
    parser = argparse.ArgumentParser(description="Script to test network configs with batfish")
    parser.add_argument(
        "--host",
        help="IP/host of the batfish server",
        default='localhost',
        type=str
    )
    parser.add_argument(
        "--candidate",
        help='Path to directory containing candidate device configuration folder',
        default='./candidate',
        type=str
    )
    parser.add_argument(
        "--failure",
        help='Path to directory containing candidate device configuration folder with injected failure conditions',
        default='./candidate-with-failure',
        type=str
    )
    parser.add_argument(
        "--log",
        help='Path to logging file',
        type=str
    )
    
    args = parser.parse_args()
    
    bf_session.coordinatorHost = args.host 
    
    bf_logger.setLevel(logging.WARN)
    
    if args.log:
        logging.basicConfig(filename=args.log, format='%(levelname)s: %(message)s', level=logging.INFO)
        console = logging.StreamHandler()
        console.setLevel(logging.ERROR)
        logging.getLogger('').addHandler(console)

    load_questions()
    bf_init_snapshot(args.candidate, name='candidate')
    bf_init_snapshot(args.failure, name='failure')

    bf_set_snapshot('candidate')
    csFailed = test_config_sanity(False)
    cpFailed = test_controlplane(False)
    dpFailed = test_dataplane(False, fromNode='leaf-3')

    logging.info("\nProgress: analysing failure conditions")
    bf_set_snapshot('failure')
    dpFailedoutage = test_dataplane(False, fromNode='leaf-3')
    rr = bfq.reducedReachability().answer(snapshot='candidate', reference_snapshot='failure')
    print_reduced_rechability(rr.get('answerElements')[0])

    

    

    return 0 if not any([cpFailed, dpFailed, csFailed, dpFailedoutage]) else 1

if __name__ == '__main__':
    sys.exit(main())

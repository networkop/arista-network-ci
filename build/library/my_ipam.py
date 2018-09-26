#!/usr/bin/python3
#coding: utf-8 -*-
# (c) 2018, Michael Kashin <mkashin@arista.com>

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}
DOCUMENTATION = ''
EXAMPLES = ''
RETURN = ''

def populate_ipam(ipam, hostname, peer_hostname, my_ip, peer_ip, my_intf, peer_intf):
    my_ipam  = ipam.get(hostname, {})
    my_link = {
        "my_ip"     : my_ip,
        "peer_ip"   : peer_ip,
        "my_intf"   : my_intf,
        "peer_intf" : peer_intf
    }
    my_ipam[peer_hostname] = my_link
    ipam[hostname] = my_ipam

def get_ips(module):
    import netaddr
    topology    = module.params.get('clos')
    buildenv    = module.params.get('env')
    ipam = dict()
    for spine, leaves in topology.items():
        for leaf, links in leaves.items():
            for link in links:
                my_link     = link[buildenv]
                ipv4_subnet = netaddr.IPNetwork(link["ipv4_subnet"])
                v4prefixlen = str(ipv4_subnet.prefixlen)
                
                spine_intf  = my_link["local"]
                leaf_intf   = my_link["remote"]
                spine_ip    = '/'.join([str(ipv4_subnet[0]), v4prefixlen])
                leaf_ip     = '/'.join([str(ipv4_subnet[-1]), v4prefixlen])

                populate_ipam(ipam, spine, leaf, spine_ip, leaf_ip, spine_intf, leaf_intf)
                populate_ipam(ipam, leaf, spine, leaf_ip, spine_ip, leaf_intf, spine_intf)
            
    return ipam

def main():
    module = AnsibleModule(
        argument_spec = dict(
            clos      = dict(required=True, type=dict),
            env       = dict(required=True, type=str)
        )
    )

    ipam = get_ips(module)
    
    module.exit_json(changed=False, ansible_facts={
        "ipam": ipam
    })

from ansible.module_utils.basic import AnsibleModule
if __name__ == '__main__':
    main()
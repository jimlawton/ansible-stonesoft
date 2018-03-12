#!/usr/bin/python
# Copyright (c) 2017 David LePage
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from smc.routing.bgp import BGPPeering

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: l3fw_cluster
short_description: Create or delete Stonesoft FW clusters
description:
  - Firewall clusters can be created with up to 16 nodes per cluster. Each
    cluster_node specified will define a unique cluster member and dictate
    the number of cluster nodes.
    You can fetch an existing engine using engine_facts and optionally save
    this as YAML to identify differences between runs.
    Interfaces and VLANs can be added, modified or removed. By default if the
    interface is not defined in the YAML, but exists on the engine, it will be
    deleted.
    To change an interface ID or VLAN id, you must delete the old and recreate
    the new interface definition. In addition, it is not possible to modify
    interfaces that have multiple IP addresses defined (they will be skipped).

version_added: '2.5'

options:
  name:
    description:
      - The name of the firewall cluster to add or delete
    required: true
  cluster_mode:
    description:
       - How to perform clustering, either balancing or standby
    choices: ['balancing', 'standby']
    default: standby
  primary_mgt:
    description:
      - Identify the interface to be specified as management
    type: int
    required: true
  backup_mgt:
    description:
      - Specify an interface by ID that will be the backup management. If the
        interface is a VLAN, specify in '2.4' format (interface 2, vlan 4).
    type: str
  primary_heartbeat:
    description:
      - Specify an interface for the primary heartbeat interface. This will
        default to the same interface as primary_mgt if not specified.
    type: str
  location:
    description:
      - Location identifier for the engine. Used when engine is behind NAT
    type: str
  interfaces:
    description:
        - Define the interface settings for this cluster interface, such as 
          address, network and node id.
    required: true
    suboptions:
      interface_id:
        description:
          - The cluster nic ID for this interface. Required.
        type: int
        required: true
      cluster_virtual:
        description:
          - The cluster virtual (shared) IP address for all cluster members. Not
            required if only creating NDI's
        type: str
        required: false
      network_value:
        description:
          - The cluster netmask for the cluster_vip. Required if I(cluster_virtual)
        type: str
      macaddress:
        description:
          - The mac address to assign to the cluster virtual IP interface. This is
            required if I(cluster_virtual)
        type: str
      zone_ref:
        description:
          - Optional zone name for this interface
        type: str
      nodes:
        description:
          - List of the nodes for this interface
        type: list
        required: true
        suboptions:
          address:
            description:
              - The IP address for this cluster node member. Required.
            type: str
            required: true
          network_value:
            description:
              - The netmask for this cluster node address. Required.
            type: str
            required: true
          nodeid:
            description:
              - The node ID for the cluster node. Required for each node in the cluster.
            type: int
            required: true
  default_nat:
    description:
      - Whether to enable default NAT on the FW. Default NAT will identify
        internal networks and use the external interface IP for outgoing
        traffic
    type: bool
    default: false
  snmp:
    description:
      - SNMP settings for the engine
    type: dict
    suboptions:
      enabled:
        description:
          - Set this to False if enabled on the engine and wanting to remove
            the configuration.
        type: bool
      snmp_agent:
        description:
          - The name of the SNMP agent from within the SMC
        type: str
        required: true
      snmp_location:
        description:
          - Optional SNMP location string to add the SNMP configuration
        type: str
        required: false
      snmp_interface:
        description:
          - A list of interface IDs to enable SNMP. If enabling on a VLAN, use
            '2.3' syntax. If omitted, snmp is enabled on all interfaces
        type: list
        required: false
  bgp:
    description:
      - If enabling BGP on the engine, provide BGP related settings
    type: dict
    suboptions:
      enabled:
        description:
          - Set to true or false to specify whether to configure BGP
        type: bool
      router_id:
        description:
          - Optional router ID to identify this BGP peer
        type: str
      autonomous_system:
        description:
          - The autonomous system for this engine. Provide additional arguments to
            allow for get or create logic
        suboptions:
          name:
            description:
                - Name of this AS
            type: str
            required: true
          as_number:
            description:
              - AS number for this BGP peer. Can be in dotted format
            type: str
            required: true
          comment:
            description:
              - Optional comment for AS
            type: str
      announced_network:
        description:
          - Announced networks identify the network and optional route map for
            internal networks announced over BGP. The list should be a dict with
            the key identifying the announced network type from SMC. The key should
            have a dict with name and route_map (optional) if the element should have
            an associated route_map.
        type: list
        choices:
            - network
            - group
            - host
      antispoofing_network:
        description:
          - Antispoofing networks are automatically added to the route antispoofing
            configuration. The dict should have a key specifying the element type from
            SMC. The dict key value should be a list of the element types by name.
        type: dict
        choices:
            - network
            - group
            - host
      bgp_peering:
        description:
          - BGP Peerings to add to specified interfaces.
        type: list
        suboptions:
          name:
            description:
              - Name of the BGP Peering
            type: str
          external_bgp_peer:
            description:
              - If the external BGP peer next hop is an external bgp peer SMC element,
                use this identifier. Otherwise use engine if its another managed SMC FW.
            type: str
          engine:
            description:
              - If the external BGP peer next hop is an engine SMC element, use this
                identifier. Otherwise use external_bgp_peer if an unmanaged endpoint.
            type: str
          interface_id:
            description:
              - List of dict with two possible valid keys interface_id and network.
                Provide interface_id to specify the interfaces where the BGP Peering
                should be placed. Optionally provide the network key value if the
                interface has multiple addresses and you want to bind to only one.
            type: str
          network:
            description:
              - Optional network to bind to on the specified interface. Use if multiple
                IP addresses exist and you want to bind to only one.
            type: str
  domain_server_address:
    description:
      - A list of IP addresses to use as DNS resolvers for the FW. Required to enable
        Antivirus, GTI and URL Filtering on the NGFW.
  antivirus:
    description:
      - Enable Anti-Virus engine on the FW
    type: bool
    default: false
  file_reputation:
    description:
      - Enable file reputation
    type: bool
    default: false
  comment:
    description:
      - Optional comment tag for the engine
    type: str
  tags:
    description:
      - Optional tags to add to this engine
    type: list
  skip_interfaces:
    description:
      - Optionally skip the analysis of interface changes. This is only relevant when
        running the playbook against an already created engine.
    type: bool
    default: false
  state:
    description:
      - Create or delete a firewall cluster
    required: false
    default: present
    choices:
      - present
      - absent
      
extends_documentation_fragment: stonesoft

requirements:
  - smc-python
author:
  - David LePage (@gabstopper)
'''

EXAMPLES = '''
- name: Firewall Template
  hosts: localhost
  gather_facts: no
  tasks:
  - name: Create a single layer 3 firewall
    l3fw_cluster:
      smc_logging:
        level: 10
        path: /Users/davidlepage/Downloads/ansible-smc.log
      antivirus: false
      backup_mgt: '2.3'
      bgp:
          announced_network:
          -   network:
                  name: foo
                  route_map: newroutemap
          -   host:
                  name: hostb
          -   group:
                  name: group1
                  route_map: myroutemap
          antispoofing_network:
              host:
              - hostb
              network:
              - network-1.1.1.0/24
              - network-172.18.1.0/24
          autonomous_system:
              as_number: 8061051
              comment: foo
              name: mynew
          bgp_peering:
          -   external_bgp_peer: bgppeer
              interface_id: '1'
              name: bgppeering
              network: 2.2.2.0/24
          -   engine: myfw
              interface_id: '2.3'
              name: bgppeering2
              network: 3.3.3.0/24
          bgp_profile: Default BGP Profile
          enabled: true
          router_id: 1.1.1.1
      cluster_mode: standby
      comment: my new firewall
      default_nat: false
      domain_server_address:
      - 8.8.8.8
      file_reputation: false
      interfaces:
      -   interface_id: '1002'
          nodes:
          -   address: 25.25.25.25
              network_value: 25.25.25.25/32
              nodeid: 1
          -   address: 25.25.25.26
              network_value: 25.25.25.25/32
              nodeid: 2
          type: tunnel_interface
      -   interface_id: '1001'
          nodes:
          -   address: 24.24.24.26
              network_value: 24.24.24.0/24
              nodeid: 2
          -   address: 24.24.24.25
              network_value: 24.24.24.0/24
              nodeid: 1
          type: tunnel_interface
      -   interface_id: '5'
      -   interface_id: '4'
          nodes:
          -   address: 5.5.5.2
              network_value: 5.5.5.0/24
              nodeid: 1
          -   address: 5.5.5.3
              network_value: 5.5.5.0/24
              nodeid: 2
          zone_ref: heartbeat
      -   interface_id: '3'
      -   interface_id: '2'
          nodes:
          -   address: 3.3.3.3
              network_value: 3.3.3.0/24
              nodeid: 2
          -   address: 3.3.3.2
              network_value: 3.3.3.0/24
              nodeid: 1
          vlan_id: '3'
      -   interface_id: '2'
          nodes:
          -   address: 4.4.4.2
              network_value: 4.4.4.0/24
              nodeid: 1
          -   address: 4.4.4.3
              network_value: 4.4.4.0/24
              nodeid: 2
          vlan_id: '4'
          zone_ref: somevlan
      -   cluster_virtual: 2.2.2.1
          interface_id: '1'
          macaddress: 02:02:02:02:02:04
          network_value: 2.2.2.0/24
          nodes:
          -   address: 2.2.2.3
              network_value: 2.2.2.0/24
              nodeid: 2
          -   address: 2.2.2.2
              network_value: 2.2.2.0/24
              nodeid: 1
          zone_ref: internal
      location: somelocation
      name: newcluster
      primary_heartbeat: '4'
      primary_mgt: '1'
      snmp:
          snmp_agent: myagent
          snmp_interface:
          - '1'
          - '2.4'
          snmp_location: newcluster
      tags:
      - footag
      #skip_interfaces: false
      #state: absent

# Delete a cluster
- name: layer 3 cluster with 3 members
  l3fw_cluster:
    name: mycluster
    state: absent
'''

RETURN = '''
changed:
  description: Whether or not the change succeeded
  returned: always
  type: bool
state:
  description: Full json definition of NGFW
  returned: always
  type: dict
'''

import traceback
from ansible.module_utils.stonesoft_util import StonesoftModuleBase, Cache  # @UnresolvedImport


try:
    from smc.core.engines import FirewallCluster
    from smc.api.exceptions import SMCException, InterfaceNotFound
    from smc.routing.bgp import AutonomousSystem
    from smc.elements.helpers import zone_helper
    from smc.elements.profiles import SNMPAgent
except ImportError:
    # Caught in StonesoftModuleBase
    pass


class YamlInterface(object):
    def __init__(self, interfaces):
        self.cluster_virtual = None
        self.interface_id = None
        self.macaddress = None
        self.network_value = None
        self.vlan_id = None
        self.zone_ref = None
        self.nodes = []
        for name, value in interfaces.items():
            if name not in ('nodes',):
                setattr(self, name, str(value))
            else:
                setattr(self, name, value)
        self.cvi_mode = 'packetdispatch' if self.cluster_virtual else None
        
    def __iter__(self):
        for node in self.nodes:
            yield node
    
    def __len__(self):
        return len(self.nodes)
    
    @property
    def is_vlan(self):
        return bool(self.vlan_id)
    
    def get_nodeid(self, nodeid):
        for nodes in self:
            if nodes.get('nodeid') == nodeid:
                return nodes
    
    def as_dict(self):
        if not self.is_vlan:
            delattr(self, 'vlan_id')
        return vars(self)

    def __repr__(self):
        return 'Interface(interface_id={}, vlan_id={})'.format(
            self.interface_id, self.vlan_id)

    
class Interfaces(object):
    """
    All interfaces defined by the YAML. Use this container
    to manage interfaces that might have single or VLAN type
    interfaces.
    
    :return: Interface
    """
    def __init__(self, interfaces):
        self._interfaces = interfaces
    
    def __iter__(self):
        for interface in self._interfaces:
            yield YamlInterface(interface)
    
    @property
    def vlan_ids(self):
        """
        Return all defined VLAN ids
        """
        return [itf.vlan_id for itf in self
                if itf.vlan_id]
    
    def get_vlan(self, vlan_id):
        """
        Get the VLAN by id
        """
        for interface in self:
            if interface.vlan_id == vlan_id:
                return interface
    
    def get(self, interface_id):
        """
        Get the interface by ID
        """
        for interface in self:
            if interface.interface_id == str(interface_id):
                return interface


def delete_vlan_interface(self):
    """
    Delete a VLAN interface. This mutates the
    interface definition directly.
    
    :param self PhysicalVlanInterface
    :param str vlan_id: vlan ID
    :return: tuple(was_changed, delete_network)
    """
    changes = False, False
    # If we have interfaces, we will need to delete the route
    if self.addresses:
        changes = True, True
    else:
        vlan_str = self.interface_id
        changes = True, False
    
    self._parent.data['vlanInterfaces'] = [
        vlan for vlan in self._parent.data['vlanInterfaces']
        if vlan.get('interface_id') != vlan_str]
    
    return changes


def create_cluster_vlan_interface(interface, yaml):
    """
    Create a new VLAN interface on the cluster. This mutates the
    interface definition directly.
    
    :param PhysicalInterface interface: the interface ref
    :param YamlInterface yaml: yaml interface
    :return: True if the create met the criteria and was added, false
        if there was no cluster address or nodes defined
    """
    if (yaml.cluster_virtual and yaml.network_value) or yaml.nodes:
        builder, interface = interface._get_builder()
        if yaml.cluster_virtual and yaml.network_value:   # Add CVI 
            builder.add_cvi_to_vlan(yaml.cluster_virtual, yaml.network_value, yaml.vlan_id) 
            if yaml.macaddress: 
                builder.macaddress = yaml.macaddress 
                builder.cvi_mode = yaml.cvi_mode 
            else: 
                builder.cvi_mode = None 
        else: # VLAN on an NDI 
            builder.add_vlan_only(yaml.vlan_id, zone_ref=yaml.zone_ref) 
        if yaml.nodes: 
            for node in yaml.nodes: 
                node.update(vlan_id=yaml.vlan_id) 
                builder.add_ndi_to_vlan(**node)
        return True
    return False
                
    
def update_cluster_vlan_interface(self, yaml):
    """
    Update the cluster VLAN interface. This mutates the
    interface definition directly.
    
    :param self PhysicalVlanInterface
    :param YamlInterface yaml: yaml serialized to interface
    :return: tuple(was_changed, delete_network)
    """
    cluster_virtual = yaml.cluster_virtual
    cluster_mask = yaml.network_value
    nodes = yaml.nodes
    
    # Tuple is defined as: (was_changed, network). If the interface
    # is changed, store the original network in the second tuple position only
    # if it is in a different network than the original so it can be removed
    # from the routing table.
    changes = False, False
    
    # Check the zone to see if we have a different value
    # If a zone exists and yaml defines a different zone,
    # change. If no interface zone exists and yaml zone
    # exists, set it. If yaml and interface zone exists,
    # compare and only change if they are not the same
    if self.zone_ref and not yaml.zone_ref:
        self.data.update(zone_ref=None)
        changes = True, False
    elif not self.zone_ref and yaml.zone_ref:
        self.zone_ref = yaml.zone_ref
        changes = True, False
    elif self.zone_ref and yaml.zone_ref:
        zone = zone_helper(yaml.zone_ref)
        if zone != self.zone_ref:
            self.zone_ref = zone
            changes = True, False
        
    # Delete all interfaces
    if not nodes and self.has_interfaces:
        self.data.update(interfaces=[])
        changes = True, True
    else:
        for interface in self.interfaces:
            if cluster_virtual and interface.nodeid is None: #CVI has no nodeid
                if cluster_virtual != interface.address:
                    interface.update(address=cluster_virtual)
                    changes = True, False
                if cluster_mask and cluster_mask != interface.network_value:
                    interface.update(network_value=cluster_mask)
                    changes = True, True
            elif nodes:
                for node in nodes:
                    if node.get('nodeid') == interface.nodeid:
                        if interface.address != node.get('address'):
                            interface.update(address=node.get('address'))
                            changes = True, False                  
                        if interface.network_value != node.get('network_value'):
                            interface.update(network_value=node.get('network_value'))
                            changes = True, True
    return changes
    

def get_or_create_asystem(as_system):
    return AutonomousSystem.get_or_create(
        name=as_system.get('name'),
        as_number=as_system.get('as_number'),
        comment=as_system.get('comment'),
        with_status=True)


def get_or_create_bgp_peering(name):
    return BGPPeering.get_or_create(
        name=name, with_status=True)


class StonesoftCluster(StonesoftModuleBase):
    def __init__(self):
        
        self.module_args = dict(
            name=dict(type='str', required=True),
            cluster_mode=dict(type='str', default='standby', choices=['standby', 'balancing']),
            interfaces=dict(type='list', default=[]),
            domain_server_address=dict(default=[], type='list'),
            location=dict(type='str'),
            bgp=dict(type='dict'),
            comment=dict(type='str'),
            log_server=dict(type='str'),
            snmp=dict(type='dict', default={}),
            default_nat=dict(default=False, type='bool'),
            antivirus=dict(default=False, type='bool'),
            file_reputation=dict(default=False, type='bool'),
            primary_mgt=dict(type='str', default='0'),
            backup_mgt=dict(type='str'),
            primary_heartbeat=dict(type='str'),
            tags=dict(type='list'),
            skip_interfaces=dict(type='bool', default=False),
            state=dict(default='present', type='str', choices=['present', 'absent'])
        )
        
        self.name = None
        self.cluster_mode = None
        self.location = None
        self.mgmt_interface = None
        self.interfaces = None
        self.domain_server_address = None
        self.bgp = None
        self.log_server = None
        self.snmp = None
        self.comment = None
        self.default_nat = None
        self.antivirus = None
        self.file_reputation = None
        self.skip_interfaces = None
        self.tags = None
        
        self.results = dict(
            changed=False,
            state=dict()
        )
            
        super(StonesoftCluster, self).__init__(self.module_args, supports_check_mode=True)
    
    def exec_module(self, **kwargs):
        state = kwargs.pop('state', 'present')
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        changed = False
        engine = self.fetch_element(FirewallCluster)
        
        if state == 'present':
            # Resolve dependencies
            if not engine:
                if not self.interfaces:
                    self.fail(msg='You must provide at least one interface '
                        'configuration to create a cluster.')
                
                node_req = ('address', 'network_value', 'nodeid')
                
                itf = Interfaces(self.interfaces)
                for interface in itf:
                    if not interface.interface_id:
                        self.fail(msg='interface_id is required for all interface '
                            'definitions')
                    for node in interface.nodes:
                        if not all(k in node for k in node_req):
                            self.fail(msg='Node missing required field. Required '
                                'fields are: %s, interface: %s' %
                                (list(node_req), interface))
                    
                # Management interface
                mgmt_interface = itf.get(self.primary_mgt)
                if not mgmt_interface:
                    self.fail(msg='Management interface is not defined. Management was '
                        'specified on interface: %s' % self.primary_mgt)
           
            # Only validate BGP if it's specifically set to enabled    
            if self.bgp and self.bgp.get('enabled', True):
                # Save the cache until the end..
                cache = Cache()
                spoofing = self.bgp.get('antispoofing_network', {})
                self.validate_antispoofing_network(spoofing)
                cache.add(spoofing)
                if cache.missing:
                    self.fail(msg='Missing elements in antispoofing configuration: %s' %
                        cache.missing)
                    
                networks = self.bgp.get('announced_network', [])
                announced_networks = self.validate_and_extract_announced(networks)
                cache.add(announced_networks)
                if cache.missing:
                    self.fail(msg='Missing elements in announced configuration: %s' % cache.missing)
                
                as_system = self.bgp.get('autonomous_system')
                if 'name' not in as_system or 'as_number' not in as_system:
                    self.fail(msg='Autonomous System requires a name and and '
                        'as_number value.')
            
                # Get external bgp peers, can be type 'engine' or 'external_bgp_peer'
                # Can also be empty if you don't want to attach a peer.
                peerings = self.bgp.get('bgp_peering', [])
                for peer in peerings:
                    if 'name' not in peer:
                        self.fail(msg='BGP Peering requires a name field to identify the '
                            'BGP Peering element')
                    if 'external_bgp_peer' not in peer and 'engine' not in peer:
                        self.fail(msg='Missing the external_bgp_peer or engine parameter '
                            'which defines the next hop for the BGP Peering')
                    if 'external_bgp_peer' in peer:
                        cache._add_entry('external_bgp_peer', peer['external_bgp_peer'])
                    elif 'engine' in peer:
                        cache._add_entry('single_fw,fw_cluster', peer['engine'])
        
                if cache.missing:
                    self.fail(msg='Missing external BGP Peering elements: %s' % cache.missing)
                
                self.cache = cache
        
        try:
                        
            if state == 'present':
                if not engine:
                    
                    interfaces = [intf.as_dict() for intf in itf
                                  if intf.interface_id != self.primary_mgt]

                    cluster = mgmt_interface.as_dict()
                    cluster.update(
                        name=self.name,
                        cluster_mode=self.cluster_mode,
                        backup_mgt=self.backup_mgt,
                        primary_heartbeat=self.primary_heartbeat,
                        log_server_ref=self.log_server,
                        domain_server_address=self.domain_server_address,
                        default_nat=self.default_nat,
                        enable_antivirus=self.antivirus,
                        enable_gti=self.file_reputation,
                        location_ref=self.location,
                        interfaces=interfaces,
                        snmp_agent=self.snmp.get('snmp_agent', None),
                        snmp_location=self.snmp.get('snmp_location', None),
                        snmp_interface=self.snmp.get('snmp_interface', []),
                        comment=self.comment)
                    
                    if self.check_mode:
                        return self.results
                
                    engine = FirewallCluster.create(**cluster)
                    changed = True
                    
                else: # Engine exists, check for modifications
                    
                    # Changes made up to check mode are done on the
                    # cached instance of the engine and not sent to SMC
                    if self.update_general(engine):
                        changed = True
                    
                    if self.snmp:
                        if self.update_snmp(engine):
                            changed = True
                            
                    if engine.cluster_mode != self.cluster_mode:
                        engine.data.update(cluster_mode=self.cluster_mode)
                        changed = True

                    if self.check_mode:
                        return self.results
                    
                    # Check engine location value
                    if self.update_location(engine):
                        changed = True
                    
                    # First actual engine update happens here
                    if changed:
                        engine.update()
                    
                    # Set skip interfaces to bypass interface checks
                    if not self.skip_interfaces:
                        interfaces, modified = self.update_interfaces(engine)
                        if modified:
                            changed = True
                    
                    if self.reset_management(engine):
                        changed = True
                    
                    # Lastly, delete top level interfaces that are not defined in 
                    # the YAML or added while looping
                    if not self.skip_interfaces:
                        for interface in engine.interface:
                            if interface.interface_id not in interfaces:
                                interface.delete()
                                changed = True
                
                ######                
                # Check for BGP configuration on either newly created engine
                # or on the existing
                ######
                if self.bgp:
                    bgp = engine.bgp
                    enable = self.bgp.get('enabled', True)
                    if not enable and bgp.status:
                        bgp.disable()
                        changed = True
                    
                    elif enable:
                        
                        if self.update_bgp(bgp):

                            autonomous_system, created = get_or_create_asystem(
                                self.bgp.get('autonomous_system'))
                            
                            if created:
                                changed = True
                            
                            bgp.disable() # Reset BGP configuration
                            bgp.enable(
                                autonomous_system,
                                announced_networks=[],
                                antispoofing_networks=self.antispoofing_format(),
                                router_id=self.bgp.get('router_id', ''),
                                bgp_profile=None) #TODO: BGP Profile
                            
                            for network in self.announced_network_format():
                                bgp.advertise_network(**network)
                            changed = True
                    
                    if changed:
                        engine.update()
                
                    if enable:
                        # BGP Peering is last since the BGP configuration may be placed
                        # on interfaces that might have been modified or added. It is
                        # possible that this could fail 
                        peerings = self.bgp.get('bgp_peering', None)
                        if peerings:
                            for peer in peerings:
                                peering, created = get_or_create_bgp_peering(
                                    peer.pop('name'))
                                if created:
                                    changed = True
                                # Update the peering on the interface
                                if self.update_bgp_peering(engine, peering, peer):
                                    changed = True
                    
                if self.tags:
                    if self.add_tags(engine, self.tags):
                        changed = True
                else:
                    if self.clear_tags(engine):
                        changed = True

                self.results['state'] = engine.data
                
            elif state == 'absent':
                if engine:
                    engine.delete()
                    changed = True
        
        except SMCException as err:
                self.fail(msg=str(err), exception=traceback.format_exc())
        
        self.results['changed'] = changed        
        return self.results
    
    def reset_management(self, engine):
        """
        Before deleting old interfaces, check the primary management
        interface setting and reset if necessary. This is done last
        in case primary management is moved to a new interface that
        was just created.
        
        :param Engine engine: engine ref
        :rtype: bool
        """
        changed = False
        management = engine.interface.get(self.primary_mgt)
        if not management.is_primary_mgt:
            engine.interface_options.set_primary_mgt(self.primary_mgt)
            changed = True
        
        if engine.interface_options.backup_mgt != self.backup_mgt:
            engine.interface_options.set_backup_mgt(self.backup_mgt)
            changed = True
        
        if engine.interface_options.primary_heartbeat != self.primary_heartbeat:
            engine.interface_options.set_primary_heartbeat(self.primary_heartbeat)
            changed = True
        return changed
    
    def update_interfaces(self, engine):
        """
        Update the interfaces on engine if necessary. You can also
        optionally set 'skip_interfaces' to bypass this check.
        
        :param engine Engine: ref to engine
        :rtype: tuple(interfaces, bool)
        """
        changed = False
        playbook = {}  # {interface_id: [interface defs]} 
        for interface in self.interfaces:
            playbook.setdefault(str(interface.get('interface_id')), []).append(
                interface)
        
        # Track interfaces defined and add new ones as they are
        # created so undefined interfaces can be deleted at the end
        playbook_interfaces = playbook.keys()
        
        # Iterate the YAML defintions
        for interface_id, interfaces in playbook.items():
            try:
                interface = engine.interface.get(interface_id)
                needs_update = False
                # Use case #1: The engine interface is defined but has no
                # interface addresses. Create as VLAN if vlan_id is defined
                # otherwise it's a non-VLAN interface
                if not interface.has_interfaces and not \
                    interface.has_vlan:
                    yaml = Interfaces(interfaces).get(interface_id)
                    
                    # Note: If the interface already exists with a VLAN
                    # specified and no addresses, you cannot convert this to
                    # a non-VLAN interface. You must delete it and recreate.
                    if yaml.vlan_id:
                        engine.physical_interface.add_ipaddress_and_vlan_to_cluster(
                            **yaml.as_dict())
                        changed = True
                        continue
                    # Create a cluster interface only if a Cluster Virtual Address,
                    # network_value and macaddress, or nodes (NDI's) are specified.
                    elif (yaml.cluster_virtual and yaml.network_value and \
                          yaml.macaddress) or len(yaml.nodes):
                        engine.physical_interface.add_cluster_virtual_interface(
                            **yaml.as_dict())
                        changed = True
                        continue    
                
                ifs = Interfaces(interfaces)
                yaml = ifs.get(interface_id)
                
                # If the engine has at least 0 interfaces but as many interfaces
                # as there are nodes (i.e. not multiple interfaces), continue.
                # It is currently not supported to modify interfaces that have
                # multiple IP addresses
                if not interface.has_vlan and  0 <= len(yaml) <= len(engine.nodes):
                    
                    # To delete nodes, remove the interface and re-add
                    if len(yaml): # Nodes are defined
                        if interface.change_cluster_interface(
                            cluster_virtual=yaml.cluster_virtual,
                            network_value=yaml.network_value,
                            macaddress=yaml.macaddress,
                            nodes=yaml.nodes, zone_ref=yaml.zone_ref,
                            vlan_id=None):
                            
                            changed = True
                    elif interface.has_interfaces:
                        # Yaml nodes are undefined, reset if addresses exist
                        interface.reset_interface()
                        changed = True
                
                elif interface.has_vlan:
                    # Collection of VLANs. It is not possible to change the VLAN
                    # ID and the interface address. You must change one or the
                    # other as it's not possible to represent the previous then
                    # new cleanly in the YAML
                    
                    routes_to_remove = []
                    vlan_interfaces = interface.vlan_interface
                    
                    for vlan in vlan_interfaces:
                        yaml = ifs.get_vlan(vlan.vlan_id)
                        # If the YAML definition for the interface exists, either
                        # create interface addresses or update existing, otherwise
                        # delete the interface.
                        if yaml is not None:
                            if not vlan.has_interfaces:
                                updated = create_cluster_vlan_interface(interface, yaml)
                                network = False
                            else:
                                updated, network = update_cluster_vlan_interface(vlan, yaml)
                        else:
                            # YAML does not define an existing interface, so
                            # delete the VLAN interface
                            updated, network = delete_vlan_interface(vlan)
                        
                        # If the interface was updated, check to see if we need
                        # to remove stale routes and add the interface ID so we
                        # can get the routing for that specific interface_id
                        if updated:
                            needs_update = True
                            if network:
                                routes_to_remove.append(
                                    vlan.interface_id)
                    
                    # Check YAML to see if VLANs are defined in YAML but not
                    # in the engine interface and create
                    interface_vlans = set(vlan_interfaces.vlan_ids)
                    missing_vlans = [x for x in ifs.vlan_ids if x not in interface_vlans]
                    for vlan in missing_vlans:
                        create_cluster_vlan_interface(interface, ifs.get_vlan(vlan))
                        needs_update = True
                          
                    if needs_update:
                        interface.update()
                        changed = True
                    
                    if routes_to_remove:
                        self.remove_routes(engine, routes_to_remove)
              
            except InterfaceNotFound:
                # Create the missing interface. Verify if it's a VLAN interface
                # versus standard
                ifs = Interfaces(interfaces)
                for itf in ifs:
                    if itf.is_vlan:
                        engine.physical_interface.add_vlan_to_cluster(
                            **itf.as_dict())
                    else:
                        engine.physical_interface.add_cluster_virtual_interface(
                            **itf.as_dict())
                    
                    changed = True
                
                playbook_interfaces.append(interface_id)
        
        return playbook, changed
    
    def remove_routes(self, engine, routes_to_remove):
        """
        Remove routes from removed interfaces
        
        :param Engine engine: engine ref
        :param list routes_to_remove: list of route interface IDs
        """
        routing = engine.routing
        for int_id in routes_to_remove:
            for route in routing:
                if route.name == 'VLAN {}'.format(int_id):
                    # If this interface has multiple networks, only
                    # delete the obsolete network, otherwise delete all
                    if len(list(route)) > 1:
                        for vlan_network in route:
                            if vlan_network.invalid:
                                vlan_network.delete()
                    else:
                        route.delete()
        
    def update_general(self, engine):
        """
        Update general settings on the engine
        
        :rtype: bool
        """
        changed = False
        if self.default_nat is not None:
            status = engine.default_nat.status
            if not status and self.default_nat:
                engine.default_nat.enable()
                changed = True
            elif status and not self.default_nat: # False or None
                engine.default_nat.disable()
                changed = True
        
        if self.file_reputation is not None:
            status = engine.file_reputation.status
            if not status and self.file_reputation:
                engine.file_reputation.enable()
                changed = True
            elif status and not self.file_reputation:
                engine.file_reputation.disable()
                changed = True
        
        if self.antivirus is not None:
            status = engine.antivirus.status
            if not status and self.antivirus:
                engine.antivirus.enable()
                changed = True
            elif status and not self.antivirus:
                engine.antivirus.disable()
                changed = True
        
        if self.domain_server_address:
            dns = [d.value for d in engine.dns]
            # DNS changes, wipe old and add new
            if set(dns) ^ set(self.domain_server_address):
                engine.data.update(domain_server_address=[])
                engine.dns.add(self.domain_server_address)
                changed = True
        return changed
                            
    def update_snmp(self, engine):
        """
        Check for updates to SNMP on the engine
        
        :rtype: bool
        """
        changed = False
        snmp = engine.snmp
        enable = self.snmp.pop('enabled', True)
        if not enable:
            if snmp.status:
                snmp.disable()
                changed = True
        else:
            if not snmp.status:
                agent = SNMPAgent(self.snmp.pop('snmp_agent', None))
                snmp.enable(snmp_agent=agent, **self.snmp)
                changed = True
            else: # Enabled check for changes
                update_snmp = False
                if snmp.agent.name != self.snmp.get('snmp_agent', ''):
                    update_snmp = True
                if snmp.location != self.snmp.get('snmp_location'):
                    update_snmp = True
                
                snmp_interfaces = [interface.interface_id for interface in snmp.interface]
                yaml_snmp_interfaces = map(str, self.snmp.get('snmp_interface', []))
                if not set(snmp_interfaces) == set(yaml_snmp_interfaces):
                    update_snmp = True
                
                if update_snmp:
                    agent = SNMPAgent(self.snmp.pop('snmp_agent', None))
                    snmp.enable(snmp_agent=agent, **self.snmp)
                    changed = True
        return changed
    
    def update_location(self, engine):
        """
        Check for an update on the engine location
        
        #TODO: rethink
        :rtype: bool
        """
        changed = False
        location = engine.location

        if not location and self.location:
            engine.location = self.location
            changed = True
        elif location and not self.location:
            engine.location = None
            changed = True
        elif location and self.location:
            if location.name != self.location:
                engine.location = self.location
                changed = True
        return changed
    
    def update_bgp(self, bgp):
        """
        Check for BGP update
        
        :param bgp BGP: reference from engine.bgp
        :rtype: bool (needs update)
        """
        if bgp.router_id != self.bgp.get('router_id', ''):
            return True
        
        bgp_profile = self.bgp.get('bgp_profile', None)
        if bgp_profile is not None and bgp_profile != bgp.profile.name:
            return True
        
        if set(bgp.data.get('antispoofing_ne_ref', [])) ^ \
            set(self.antispoofing_format()):
            return True
        
        # Announced networks
        current = bgp.data.get('bgp', {}).get('announced_ne_setting', [])
        current_dict = {entry.get('announced_ne_ref'): entry.get('announced_rm_ref')
            for entry in current}
        
        # Put the specified dict into a format to compare
        new_dict = {entry.get('network'): entry.get('route_map')
            for entry in self.announced_network_format()}
        
        if cmp(current_dict, new_dict) != 0:
            return True
        return False
    
    def update_bgp_peering(self, engine, bgp_peering, peering_dict):
        """
        Update BGP Peering on the interface. Only update if the
        peering isn't already there.
        
        :param Engine engine: engine ref
        :param BGPPeering bgp_peering: peering ref
        :param dict peering_dict: list of interfaces to add to
        :rtype: bool
        """
        if 'external_bgp_peer' in peering_dict:
            extpeer = self.cache.get('external_bgp_peer', peering_dict.get('external_bgp_peer'))
        elif 'engine' in peering_dict:
            extpeer = self.cache.get('single_fw,fw_cluster', peering_dict.get('engine'))
        
        changed = False
        interface_id = peering_dict.get('interface_id')
        network = peering_dict.get('network')
        routing = engine.routing.get(interface_id)
            
        interface_peerings = list(routing.bgp_peerings)
        needs_update = False
        if interface_peerings:
            for _, net, peering in interface_peerings:
                if network and net.ip == network:
                    if peering.name != bgp_peering.name:
                        needs_update = True
                else:
                    if bgp_peering.name != peering.name:
                        needs_update = True
        else:
            needs_update = True
        
        if needs_update:
            routing.add_bgp_peering(
                bgp_peering, extpeer, network)
            changed = True
       
        return changed
        
    def validate_antispoofing_network(self, s):
        """
        Validate the input antispoofing format:
        
        Expected format for antispoofing networks:
            {'network': [net1, net2],
             'host': [hosta, hostb}]}
        
        :return: None
        """
        valid = ('network', 'group', 'host')
        for typeof, values in s.items():
            if typeof not in valid:
                self.fail(msg='Antispoofing network definition used an invalid '
                    'element type: %s, valid: %s' % (typeof, list(valid)))
            elif not hasattr(values, '__iter__'):
                self.fail(msg='Antispoofing network value should be in list '
                    'format')
    
    def validate_and_extract_announced(self, s):
        """
        Validate the announced network structure and format for
        inclusion into the cache for later use.
        
        Expected format for announced networks:
            [{'network': {'name': u'foo',
                          'route_map': u'myroutemap'}},
             {'host': {'name': u'All Routers (Site-Local)'}}]
        
        :return: dict with key: typeof, values=['name1', 'name2']
        """
        valid = ('network', 'group', 'host')
        for_cache = {}
        for announced in s:
            for typeof, dict_value in announced.items():
                if not isinstance(dict_value, dict):
                    self.fail(msg='Announced network type should be defined with '
                        'name and optionally route_map as a dict.')
                if typeof not in valid:
                    self.fail(msg='Invalid announced network was provided: %s, '
                        'valid types: %s' % (typeof, list(valid)))
                if 'name' not in dict_value:
                    self.fail(msg='Announced Networks requires a name')
                if 'route_map' in dict_value:
                    for_cache.setdefault('route_map', []).append(
                        dict_value['route_map'])
                for_cache.setdefault(typeof, []).append(
                    dict_value['name'])
        return for_cache
        
    def antispoofing_format(self):
        """
        Get the antispoofing format
        
        :rtype: list of href
        """
        return [self.cache.get(typeof, value).href
            for typeof, v in self.bgp.get('antispoofing_network', {}).items()
            for value in v]
    
    def announced_network_format(self):
        """
        Get the announced network format
        
        :rtype: list(dict)
        """
        announced_ne_setting = []
        for entry in self.bgp.get('announced_network', []):
            for typeof, dict_value in entry.items():
                name = self.cache.get(typeof, dict_value.get('name'))
                route_map = self.cache.get('route_map', dict_value.get('route_map'))
                announced_ne_setting.append(
                    {'network': name.href, 'route_map': route_map if not route_map else route_map.href})
        return announced_ne_setting

    
def main():
    StonesoftCluster()
    
if __name__ == '__main__':
    main()

        
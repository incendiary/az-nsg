import requests
import json
import xml.etree.ElementTree
from lxml import html
import sys

def get_xml_url_from_microsoft(url):
    print "[*] Getting the xml url from the MS download page"
    r = requests.get(url)
    webpage = html.fromstring(r.content)
    for url in webpage.xpath('//a/@href'):
        if 'PublicIPs' in url:
            return url
    print "Error in get_xml_url_from_microsoft"
    exit()

def get_xml_from_microsoft(url, file_name):
    print "[*] Getting the actual xml"
    r = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        f.write(r.content)

def parse_xml(xml_file_name):
    print "[*] parsing the xml"
    xmlobj = xml.etree.ElementTree.parse(xml_file_name).getroot()
    return xmlobj

def find_ip_ranges(xmlobj, target_region):
    subnets = []
    for region in xmlobj.findall('Region'):
        name = region.get('Name')

        if name == target_region:
            print "[*] Target Region Located: %s" % (name)

            for iprange in region:
                subnet = iprange.get('Subnet')
                #print "[*] %s" % (subnet)
                subnets.append(subnet)

    return subnets

def format_name(name, direction):
    # takes the ip address and formats it for the name value
    n = "az_nsg_automated_%s_%s" % (name.replace('/', '_'), direction)
    return n

def generate_rules(azsubnets, resource_groups_nsg_names, start_priority, directions, protocols):
    print "[*] Generating ruleset"
    rulelist = []
    for direction in directions:
        # want to split on direction so that priority can be reset for both inbound and outbound rules
        priority = start_priority

        for resource_group, nsg_names_subnets_dict_list in resource_groups_nsg_names.iteritems():

            for nsg_names_subnets_dict in nsg_names_subnets_dict_list:

                for nsg_name, subnet_list in nsg_names_subnets_dict.iteritems():

                    for subnet in subnet_list:

                        for azsubnet in azsubnets:

                            for protocol in protocols:

                                rule = "az network nsg rule create " \
                                      "-g %s --nsg-name %s " \
                                      "--priority %i " \
                                      "--protocol %s " \
                                      "--destination-port-range '*' " % \
                                      (resource_group, nsg_name, priority, protocol)

                                # direction - if inbound azsubnets = source, if outbound, destination.
                                # Inverse for subnets

                                if direction == "Inbound":
                                    rule += "-n %s " \
                                            "--description 'automated Inbound rule for access to azure resources' " \
                                            "--direction 'Inbound' " \
                                            "--source-address-prefix %s " \
                                            "--destination-address-prefix %s " %(format_name(azsubnet, 'Inbound'),
                                                                                 azsubnet, subnet)

                                elif direction == "Outbound":
                                    rule += "-n %s " \
                                            "--description 'automated Outbound rule for access to azure resources' " \
                                            "--direction 'Outbound' " \
                                            "--source-address-prefix %s " \
                                            "--destination-address-prefix %s " % (format_name(azsubnet, 'OutBound'),
                                                                                  subnet, azsubnet)

                                rulelist.append(rule)

                                priority += 1
    return rulelist

def main():
    #Some vars

    source_url = "https://www.microsoft.com/en-us/download/confirmation.aspx?id=41653"
    xml_file_name = "current.xml"
    target_region = "europenorth"
    outputfile = "output.txt"

    start_priority = 3000
    directions = ['Inbound', 'Outbound']
    protocol = ["'*'"] # list values can be * TCP or UDP

    #expected structure is a dictonary, with the key identifying the resource group and the value identifying a list of
    #nsg within that resource group.  include as a list even if only 1 nsg. each NSG is a key, value pair value.  Key identifies
    #the name, value is a list with the IP address ranges used for destination or source in that NSG
    #may hit resource limits if multiple netblocks

    resource_groups_nsg_names = {
        "resourcegroup1":
            [
                {
                    "a-tier-nsg": ["10.0.0.0/24"],
                    "b-tier-nsg": ["172.16.0.0/24"],
                    "c-tier-nsg": ["192.168.0.0/24"],
                }
            ],
        "resourcegroup2":
            [
                {
                    "x-tier-nsg": ["10.0.0.0/24"],
                    "y-tier-nsg": ["172.16.0.0/24"],
                    "z-tier-nsg": ["192.168.0.0/24"],
                }
            ],
    }

    url = get_xml_url_from_microsoft(source_url)
    get_xml_from_microsoft(url, xml_file_name)
    xmlobj = parse_xml(xml_file_name)
    azsubnets = find_ip_ranges(xmlobj, target_region)

    rules = generate_rules(azsubnets, resource_groups_nsg_names, start_priority, directions, protocol)

    print "[*] Writing rules to file for review"

    file = open(outputfile, 'w')
    for rule in rules:
        file.write("%s\n" % rule)

if __name__ == "__main__":
    main()
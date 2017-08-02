# az-nsg
Automated creation of rules for azure, to allow connection to regional azure resources in otherwise restricted enviroments


###### Example run below:


    virtualenv venv
    source venv/bin/activate
    pip install -r requirements

    python az-nsg.py
    [*] Getting the xml url from the MS download page
    [*] Getting the actual xml
    [*] parsing the xml
    [*] Target Region Located: europenorth
    [*] Generating ruleset
    [*] Writing rules to file for review

###### Example output:

    az network nsg rule create -g resourcegroup1 --nsg-name a-tier-nsg -n az_nsg_automated_10.0.0.0_24 --priority 3000 --protocol '*' --description 'automated rule for access to azure resources' --direction 'Inbound' --source-address-prefix 13.70.209.0/24 --destination-address-prefix 10.0.0.0/24
    az network nsg rule create -g resourcegroup1 --nsg-name a-tier-nsg -n az_nsg_automated_10.0.0.0_24 --priority 3001 --protocol '*' --description 'automated rule for access to azure resources' --direction 'Inbound' --source-address-prefix 40.90.141.128/27 --destination-address-prefix 10.0.0.0/24
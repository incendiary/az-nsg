# az-nsg

> **Note:** This is a Python 2 script written circa 2017. It is preserved as-is for reference. The Azure IP ranges XML format and the Microsoft download page URL it depends on may have changed since it was written.

Generates Azure CLI (`az network nsg rule`) commands to allow inbound/outbound access between your Azure NSG-protected subnets and the published IP ranges for a specific Azure region. Useful in environments where NSG rules must be tightly scoped and Azure's regional IP ranges change frequently.

---

## How it works

1. Fetches the Azure Public IP Ranges XML from the [Microsoft Download Center](https://www.microsoft.com/en-us/download/details.aspx?id=41653)
2. Parses it to find all CIDR blocks for the target region
3. For each combination of Azure subnet × your protected subnet, generates `az network nsg rule create` commands
4. Writes the commands to an output file for review before applying

```
[Microsoft Download Page]
        │
        ▼
  current.xml (Azure public IP ranges)
        │
        ▼
  Parse for target region (e.g. europenorth)
        │
        ▼
  Generate NSG rule commands per subnet pair
        │
        ▼
  output.txt  ←  Review, then pipe to az CLI
```

---

## Prerequisites

- Python 2.7
- `pip install -r requirements` (installs `requests`, `lxml`)

---

## Configuration

Edit the variables at the top of `main()` in `az-nsg.py` before running:

```python
target_region = "europenorth"        # Azure region name from the XML
outputfile    = "output.txt"         # Where to write the generated rules
start_priority = 3000                # Starting NSG rule priority
directions    = ['Inbound', 'Outbound']
protocol      = ["'*'"]              # '*', 'TCP', or 'UDP'

resource_groups_nsg_names = {
    "your-resource-group": [
        {
            "your-nsg-name": ["10.0.0.0/24"],  # subnets behind this NSG
        }
    ],
}
```

> Azure region names used in the XML (e.g. `europenorth`, `useast`) differ from the display names in the portal. Check the downloaded XML for the exact string.

---

## Usage

```bash
virtualenv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements

python az-nsg.py
```

Output is written to `output.txt`. Review the generated commands before applying:

```bash
# Apply a single rule to verify, then batch the rest
az network nsg rule create -g <rg> --nsg-name <nsg> -n az_nsg_automated_... ...
```

---

## Example output

```
az network nsg rule create -g resourcegroup1 --nsg-name a-tier-nsg \
  -n az_nsg_automated_13.70.209.0_24_Inbound --priority 3000 \
  --protocol '*' \
  --description 'automated Inbound rule for access to azure resources' \
  --direction 'Inbound' \
  --source-address-prefix 13.70.209.0/24 \
  --destination-address-prefix 10.0.0.0/24
```

---

## Roadmap

- [ ] Port to Python 3
- [ ] Accept region and NSG config from a config file rather than hardcoded in `main()`
- [ ] Validate that the Microsoft download page URL is still current

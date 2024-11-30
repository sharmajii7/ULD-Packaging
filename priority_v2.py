import time
from py3dbp import Packer, Bin, Item, Painter
from subroutine_v2 import subroutine

start = time.time()

# Function to parse the input file
def parse_file(filename):
    ulds = []
    packages = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("ULD"):
                continue
            if line.startswith("Package"):
                continue
            if line.startswith("U"):
                parts = line.split(',')
                ulds.append({
                    'id': parts[0],
                    'length': int(parts[1]),
                    'width': int(parts[2]),
                    'height': int(parts[3]),
                    'weightlimit': int(parts[4]),
                    'volume': int(parts[1]) * int(parts[2]) * int(parts[3]),
                })
            if line.startswith("P"):
                parts = line.split(',')
                packages.append({
                    'id': parts[0],
                    'length': int(parts[1]),
                    'width': int(parts[2]),
                    'height': int(parts[3]),
                    'weight': int(parts[4]),
                    'type': parts[5],
                    'delaycost': int(parts[6]) if parts[6] != '-' else 0,
                    'volume': int(parts[1]) * int(parts[2]) * int(parts[3]),
                })
    return ulds, packages

# Parse the input file
filename = "Challange_FedEx.txt"
ulds, packages = parse_file(filename)

packids = []

# Sort ULDs
ulds.sort(key=lambda u: -u['volume'])

# Sort packages and packids
packages.sort(key=lambda p: (p['type'] != "Priority", -p['delaycost']))
packids = [pkg['id'] for pkg in packages]  # Reorder packids based on sorted packages

# Count Priority packages
priority_count = sum(1 for pkg in packages if pkg['type'] == "Priority")

# Filter Priority packages
priority_packages = [pkg for pkg in packages if pkg['type'] == "Priority"]
priority_packids = [pkg['id'] for pkg in priority_packages]  # Get IDs for Priority packages

# Call subroutine with only Priority packages
unpacked_count, bin_assignments, unpacked_items = subroutine(ulds=ulds, packages=priority_packages, packids=priority_packids)

# print("Number of unpacked items:", unpacked_count)
print("Items assigned to each bin:", bin_assignments)
print("Unpacked items:", unpacked_items)



# for i in range(len(packids)):
#     unpacked = subroutine(ulds=ulds, packages=packages, packids=packids)
    

stop = time.time()
print('Time Taken: ', stop - start)

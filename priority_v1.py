import time
from py3dbp import Packer, Bin, Item, Painter
from subroutine import subcalc

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

# for i in range(len(packids)):
#     # Call subroutine
#     subcalc(ulds=ulds, packages=packages, packids=packids)
subcalc(ulds=ulds, packages=packages, packids=packids)

stop = time.time()
print('Time Taken: ', stop - start)

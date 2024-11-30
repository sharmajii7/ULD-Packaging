import time
from subroutine_v2 import subroutine
from economyassign import economyassign
from visualisation import visualisation

start = time.time()

# Function to parse the input file
def parse_file(filename):
    ulds = []
    packages = []
    k = 0
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("K"):
                k = int(line.split('=')[1].split(',')[0].strip())
                continue
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
    return ulds, packages, k

# Parse the input file
filename = "Challange_FedEx.txt"
ulds, packages, k = parse_file(filename)

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

totcost = 0

print("SPACE UTILISATION BY PRIORITY PACKAGES: ")

# Call subroutine with only Priority packages
unpacked_count, bin_assignments = subroutine(ulds=ulds, packages=priority_packages, packids=priority_packids)
# print("Number of unpacked items:", unpacked_count)
# print("Items assigned to each bin:", bin_assignments)
print("Number of priorty packages not packed: ", unpacked_count)

# Count non-empty bins
non_empty_bins = sum(1 for bin_id, items in bin_assignments.items() if items)
totcost += k * non_empty_bins

print("\n\nPackages not assigned to any ULD: ")

tot_unpacked = 0
for i in range(priority_count, len(packids)):
    current_package = packages[i]  # The current package to assign
    assigned = False  # Track if the package has been assigned

    for uld in ulds:  # Check each ULD individually
        # Get the packages already assigned to this ULD
        already_assigned = bin_assignments.get(uld['id'], [])
        assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

        # Add the current package to the assigned list temporarily
        assigned_packages.append(current_package)

        # Call subroutine with this ULD and the combined packages
        unpacked_count = economyassign(
            ulds=[uld],  # Use the current ULD
            packages=assigned_packages,  # Include already assigned + current package
            packids=[pkg['id'] for pkg in assigned_packages]  # IDs of combined packages
        )

        # If all items are packed successfully (no unpacked items), assign the package
        if unpacked_count == 0:
            bin_assignments[uld['id']].append(current_package['id'])  # Update the assignments
            assigned = True
            break  # No need to check further ULDs for this package

    # If the package was not assigned to any ULD
    if not assigned:
        tot_unpacked += 1
        totcost += current_package['delaycost']
        # print(f"Package {current_package['id']} could not be assigned to any ULD.")
        print(current_package['id'], end=", ", flush=True)
    
print("\n\nOVERALL SPACE UTILISATION: ")

for uld in ulds:
    # Get the packages already assigned to this ULD
    already_assigned = bin_assignments.get(uld['id'], [])
    assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

    # Call subroutine with this ULD
    unpacked_count = visualisation(
        ulds=[uld],  # Use the current ULD
        packages=assigned_packages,  # Include already assigned + current package
        packids=[pkg['id'] for pkg in assigned_packages]  # IDs of combined packages
    )

print("\nTotal cost: ", totcost)
print("Total unpacked items: ", tot_unpacked )
stop = time.time()
print('Time Taken: ', stop - start)

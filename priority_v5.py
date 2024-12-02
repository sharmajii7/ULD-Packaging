import time
import concurrent.futures
from subroutine_v2 import subroutine
from economyassign import economyassign
from visualisation_v2 import visualisation

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
            if line.startswith("ULD") or line.startswith("Package"):
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

def assign_package_to_uld(current_package, ulds, bin_assignments, all_packages):
    """
    Try to assign a single package to a ULD
    
    Args:
        current_package (dict): Package to be assigned
        ulds (list): Available ULDs
        bin_assignments (dict): Current package assignments to ULDs
        all_packages (list): Complete list of packages
    
    Returns:
        tuple: (package_id, assigned_uld_id, total_cost)
    """
    for uld in ulds:
        # Get the packages already assigned to this ULD
        already_assigned = bin_assignments.get(uld['id'], [])
        assigned_packages = [pkg for pkg in all_packages if pkg['id'] in already_assigned]

        # Add the current package to the assigned list temporarily
        assigned_packages.append(current_package)

        # Call economyassign with this ULD and the combined packages
        unpacked_count = economyassign(
            ulds=[uld],  # Use the current ULD
            packages=assigned_packages,  # Include already assigned + current package
            packids=[pkg['id'] for pkg in assigned_packages]  # IDs of combined packages
        )

        # If all items are packed successfully (no unpacked items), assign the package
        if unpacked_count == 0:
            return (current_package['id'], uld['id'], 0)  # Successfully assigned
    
    # If package was not assigned to any ULD
    return (current_package['id'], None, current_package['delaycost'])

def main():
    start = time.time()

    # Parse the input file
    filename = "Challange_FedEx.txt"
    ulds, packages, k = parse_file(filename)

    # Sort ULDs and packages
    ulds.sort(key=lambda u: -u['volume'])
    packages.sort(key=lambda p: (p['type'] != "Priority", -p['delaycost']))
    packids = [pkg['id'] for pkg in packages]

    # Count Priority packages
    priority_count = sum(1 for pkg in packages if pkg['type'] == "Priority")
    priority_packages = [pkg for pkg in packages if pkg['type'] == "Priority"]
    priority_packids = [pkg['id'] for pkg in priority_packages]

    totcost = 0

    print("SPACE UTILISATION BY PRIORITY PACKAGES: ")

    # Call subroutine with only Priority packages
    unpacked_count, bin_assignments = subroutine(ulds=ulds, packages=priority_packages, packids=priority_packids)
    print("Number of priority packages not packed: ", unpacked_count)

    # Count non-empty bins
    non_empty_bins = sum(1 for bin_id, items in bin_assignments.items() if items)
    totcost += k * non_empty_bins    

    print("\n\nPackages not assigned to any ULD: ")

    # Parallel package assignment for non-priority packages
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Create a list of futures for package assignments
        futures = [
            executor.submit(assign_package_to_uld, 
                            packages[i], 
                            ulds, 
                            bin_assignments, 
                            packages) 
            for i in range(priority_count, len(packids))
        ]

        tot_unpacked = 0
        unpackedids = []
        
        # Process results
        for future in concurrent.futures.as_completed(futures):
            package_id, uld_id, cost = future.result()
            
            if uld_id is None:
                # Package could not be assigned
                tot_unpacked += 1
                totcost += cost
                unpackedids.append(package_id)
                print(package_id, end=", ", flush=True)
            else:
                # Update bin assignments if package was assigned
                bin_assignments[uld_id].append(package_id)
    
    tot_packed = len(packages) - tot_unpacked
    firstline = str(totcost) + "," + str(tot_packed) + "," + str(non_empty_bins) + "\n"

    print("\n\nOVERALL SPACE UTILISATION: ")
    
    alllines = []
    
    # Setting coordinates to -1 for unpacked items
    for uld in unpackedids:
        line = str(uld) + ",NONE,-1,-1,-1,-1,-1,-1\n"
        alllines.append(line)
    
    for uld in ulds:
        # Get the packages already assigned to this ULD
        already_assigned = bin_assignments.get(uld['id'], [])
        assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

        # Call visualization for each ULD
        lines = visualisation(
            ulds=[uld],
            packages=assigned_packages,
            packids=[pkg['id'] for pkg in assigned_packages]
        )
        alllines.extend(lines)

    print("\nTotal cost: ", totcost)
    print("Total unpacked items: ", tot_unpacked)    
    
    stop = time.time()
    print('Time Taken: ', stop - start)
    
    alllines = sorted(alllines, key=lambda x: int(x.split(',')[0].split('-')[1]))
    with open('output.txt', 'w+') as file:
        file.write(firstline)
        file.writelines(alllines)

if __name__ == "__main__":
    main()
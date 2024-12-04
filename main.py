import time
from packageAssigner import packageAssigner
from visualiser import visualiser
from spaceUtilisation import spaceUtilisation

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
                if(len(parts) != 5):
                    print("Please enter the ULD details in the correct format")
                    quit()
                if(parts[0] == ""):
                    print("Ensure that ULD has an ID")
                    quit()
                if((parts[1].isnumeric() == 0) or int(parts[1]) <= 0):
                    print(f"ULD: {parts[0]} needs to have positive length")
                    quit()
                if((parts[2].isnumeric() == 0) or int(parts[2]) <= 0):
                    print(f"ULD: {parts[0]} needs to have positive width")
                    quit()
                if((parts[3].isnumeric() == 0) or int(parts[3]) <= 0):
                    print(f"ULD: {parts[0]} needs to have positive height")
                    quit()
                if((parts[4].isnumeric() == 0) or int(parts[4]) < 0):
                    print(f"ULD: {parts[0]} needs to have non-negative weightlimit")
                    quit()
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
                if(len(parts) != 7):
                    print("Please enter the Package details in the correct format")
                    quit()
                if(parts[0] == ""):
                    print("Ensure that Package has an ID")
                    quit()
                if((parts[1].isnumeric() == 0) or int(parts[1]) <= 0):
                    print(f"Package: {parts[0]} needs to have positive length")
                    quit()
                if((parts[2].isnumeric() == 0) or int(parts[2]) <= 0):
                    print(f"Package: {parts[0]} needs to have positive width")
                    quit()
                if((parts[3].isnumeric() == 0) or int(parts[3]) <= 0):
                    print(f"Package: {parts[0]} needs to have positive height")
                    quit()
                if((parts[4].isnumeric() == 0) or int(parts[4]) <= 0):
                    print(f"Package: {parts[0]} needs to have positive weight")
                    quit()
                if(parts[5] != "Priority" and parts[5] != "Economy" and parts[5] != "P" and parts[5] != "E"):
                    print(f"Package: {parts[0]} needs to have a type (Priority/Economy)")
                    quit()
                if(parts[5] == ""):
                    parts[5] = "Economy"
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

        # Call packageAssigner with this ULD and the combined packages
        unpacked_count = packageAssigner(
            ulds=[uld],  # Use the current ULD
            packages=assigned_packages,  # Include already assigned + current package
            packids=[pkg['id'] for pkg in assigned_packages]  # IDs of combined packages
        )

        # If all items are packed successfully (no unpacked items), assign the package
        if unpacked_count == 0:
            return (current_package['id'], uld['id'], 0)  # Successfully assigned
    
    # If package was not assigned to any ULD
    return (current_package['id'], None, current_package['delaycost'])

def main(x = 5, y = 2, z = 1):
    start = time.time()

    # Parse the input file
    # filename = "Challange_FedEx_test.txt"
    filename = "Challange_FedEx.txt"
    ulds, packages, k = parse_file(filename)

    # Sort ULDs and packages
    ulds.sort(key=lambda u: (-u['volume'], -u['weightlimit']))
    # packages.sort(key=lambda p: (p['type'] != "Priority", -p['delaycost']))
    # packages.sort(
    #     key=lambda p: (
    #         p['type'] != "Priority",  # Sort Priority packages first
    #         -(pow(p['volume'], w) * pow(p['weight'], d)) if p['type'] == "Priority" else -(pow(p['delaycost'], x) / (pow(p['volume'], y) * pow(p['weight'], z)))  # Sort by decreasing volume for Priority, and by decreasing delaycost for others
    #     )
    # )
    packages.sort(
        key=lambda p: (
            p['type'] != "Priority",  # Sort Priority packages first
            -(max(p['length'], p['height'], p['width'])) if p['type'] == "Priority" else -(pow(p['delaycost'], x) / (pow(p['volume'], y) * pow(p['weight'], z)))  # Sort by decreasing volume for Priority, and by decreasing delaycost for others
        )
    )
    packids = [pkg['id'] for pkg in packages]

    # Count Priority packages
    priority_count = sum(1 for pkg in packages if pkg['type'] == "Priority")
    priority_packages = [pkg for pkg in packages if pkg['type'] == "Priority"]
    priority_packids = [pkg['id'] for pkg in priority_packages]

    totcost = 0

    print("SPACE UTILISATION BY PRIORITY PACKAGES: ")

    # Call subroutine with only Priority packages
    # unpacked_count, bin_assignments = subroutine(ulds=ulds, packages=priority_packages, packids=priority_packids)
    
    bin_assignments = {}
    
    for uld in ulds:
        bin_assignments[uld['id']] = []
    
    for i in range(priority_count):
        current_package = packages[i]  # The current package to assign
        assigned = False  # Track if the package has been assigned

        # # Sort ULDs by least available volume
        # ulds.sort(
        #     key=lambda u: -(sum(pkg['volume'] for pkg in packages if pkg['id'] in bin_assignments[u['id']]))
        # )

        for uld in ulds:  # Check each ULD individually
            # Get the packages already assigned to this ULD
            already_assigned = bin_assignments.get(uld['id'], [])
            assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

            # Add the current package to the assigned list temporarily
            assigned_packages.append(current_package)

            # Call subroutine with this ULD and the combined packages
            unpacked_count = packageAssigner(
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
            unpacked_count += 1
            print(f"Priority package {current_package['id']} could not be assigned to any ULD.")
            
    for uld in ulds:
        # Get the packages already assigned to this ULD
        already_assigned = bin_assignments.get(uld['id'], [])
        assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

        # Call spaceutilisation for each ULD
        spaceUtilisation(
            ulds=[uld],
            packages=assigned_packages,
            packids=[pkg['id'] for pkg in assigned_packages]
        )
    print("Number of priority packages not packed: ", unpacked_count)

    # Count non-empty bins
    non_empty_bins = sum(1 for bin_id, items in bin_assignments.items() if items)
    totcost += k * non_empty_bins    

    print("\n\nPackages not assigned to any ULD: ")
    
    unpackedids = []
                
    tot_unpacked = 0
    for i in range(priority_count, len(packids)):
        current_package = packages[i]  # The current package to assign
        assigned = False  # Track if the package has been assigned
        
        # Sort ULDs by least available volume
        # ulds.sort(
        #     key=lambda u: -(sum(pkg['volume'] for pkg in packages if pkg['id'] in bin_assignments[u['id']]))
        # )

        for uld in ulds:  # Check each ULD individually
            # Get the packages already assigned to this ULD
            already_assigned = bin_assignments.get(uld['id'], [])
            assigned_packages = [pkg for pkg in packages if pkg['id'] in already_assigned]

            # Add the current package to the assigned list temporarily
            assigned_packages.append(current_package)

            # Call subroutine with this ULD and the combined packages
            unpacked_count = packageAssigner(
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
            unpackedids.append(current_package['id'])
            totcost += current_package['delaycost']
            # print(f"Package {current_package['id']} could not be assigned to any ULD.")
            print(current_package['id'], end=", ", flush=True)
    
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
        lines = visualiser(
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
    with open('output.txt', 'w') as file:
        file.write(firstline)
        file.writelines(alllines)

if __name__ == "__main__":
    main(5, 2, 1)
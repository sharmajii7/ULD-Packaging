from py3dbp import Packer, Bin, Item

def subroutine(ulds, packages, packids):
    # Initialize the packer
    packer = Packer()

    # Add ULDs (bins) to the packer
    for uld in ulds:
        packer.addBin(Bin(partno=uld['id'], WHD=(uld['length'], uld['width'], uld['height']),
                          max_weight=uld['weightlimit'], corner=0, put_type=1))

    # Add packages (items) to the packer
    for package in packages:
        packer.addItem(Item(partno=package['id'], name=package['id'], typeof='cube', 
                            WHD=(package['length'], package['width'], package['height']),
                            weight=package['weight'], level=1, loadbear=100, updown=True, color='#FFFF37'))

    # Calculate packing 
    packer.pack(
        bigger_first=True,
        distribute_items=True,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0.6,
        number_of_decimals=0
    )

    # Initialize storage for results
    bin_assignments = {}  # To store items assigned to each bin

    repeated = ''
    for b in packer.bins:
        print(b.partno)
        volume = b.width * b.height * b.depth

        # Store items for this bin
        bin_assignments[b.partno] = []

        volume_t = 0
        for item in b.items:
            if packids.count(item.partno) != 0:
                packids.remove(item.partno)
            else:
                repeated += '{}, '.format(item.partno)

            bin_assignments[b.partno].append(item.partno)  # Add item to this bin's list
            volume_t += float(item.width) * float(item.height) * float(item.depth)

        volume_f = 0
        for item in b.unfitted_items:
            volume_f += float(item.width) * float(item.height) * float(item.depth)

        print('space utilization: {}%'.format(round(volume_t / float(volume) * 100, 2)))
        print('residual volume: ', float(volume) - volume_t)
        print('unpack item volume: ', volume_f)
        print("gravity distribution: ", b.gravity)
        print("***************************************************")

    print("Number of unpacked items: ", len(packids))
    print("Repeated packing: ", repeated)
    return len(packids), bin_assignments

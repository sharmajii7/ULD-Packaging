from py3dbp import Packer, Bin, Item

def economyassign(ulds, packages, packids):
    # Initialize the packer
    packer = Packer()

    # Add ULDs (bins) to the packer
    for uld in ulds:
        # packer.addBin(Bin(partno=uld['id'], WHD=(uld['length'], uld['width'], uld['height']), max_weight=99999, corner=0, put_type=1))
        packer.addBin(Bin(partno=uld['id'], WHD=(uld['length'], uld['width'], uld['height']), max_weight=uld['weightlimit'], corner=0, put_type=1))

    # Add packages (items) to the packer
    for package in packages:
        packer.addItem(Item(partno=package['id'], name=package['id'], typeof='cube', 
                            WHD=(package['length'], package['width'], package['height']),
                            weight=package['weight'], level=1, loadbear=100, updown=True, color='#FFFF37'))

    # calculate packing 
    packer.pack(
        bigger_first=True,
        distribute_items=True,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0.6,
        number_of_decimals=0
    )

    repeated = ''
    # print result
    for b in packer.bins:
        for item in b.items:
            if(packids.count(item.partno) != 0):
                packids.remove(item.partno)
            else:
                repeated += '{}, '.format(item.partno)
        for item in b.unfitted_items:
            return 1
    return len(packids)

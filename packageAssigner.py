from Subroutine import Assigner, ULD, Package

def packageAssigner(ulds, packages, packids):
    # Initialize the packer
    packer = Assigner()

    # Add ULDs (ULDs) to the packer
    for uld in ulds:
        packer.addULD(ULD(partno=uld['id'], WHD=(uld['length'], uld['width'], uld['height']), max_weight=uld['weightlimit']))

    # Add packages (packages) to the packer
    for package in packages:
        if(package['type'] == "Priority"):
            packer.addPackage(Package(partno=package['id'], name=package['id'], 
                            WHD=(package['length'], package['width'], package['height']),
                            weight=package['weight'], loadbear=100, updown=True, color='olive',type='Priority'))
        else:
            packer.addPackage(Package(partno=package['id'], name=package['id'], 
                            WHD=(package['length'], package['width'], package['height']),
                            weight=package['weight'], loadbear=100, updown=True, color='pink',type='Economy'))

    # calculate packing 
    packer.pack(
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0.6
    )

    repeated = ''
    # print result
    for b in packer.ULDs:
        for item in b.packages:
            if(packids.count(item.partno) != 0):
                packids.remove(item.partno)
            else:
                repeated += '{}, '.format(item.partno)
        for item in b.unfitted_packages:
            return 1
    return len(packids)

from Subroutine import Assigner, ULD, Package

def spaceUtilisation(ulds, packages, packids,s_s_a_r =0.6):
    # Initialize the packer
    packer = Assigner()

    # Add ULDs (bins) to the packer
    for uld in ulds:
        packer.addULD(ULD(partno=uld['id'], WHD=(uld['length'], uld['width'], uld['height']),
                          max_weight=uld['weightlimit']))

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

    # Calculate packing 
    packer.pack(
        fix_point=True,
        check_stable=True,
        support_surface_ratio=s_s_a_r
    )

    repeated = ''
    lines = []
    for b in packer.ULDs:
        print(b.partno)
        volume = b.width * b.height * b.depth

        volume_t = 0
        for package in b.packages:
            if packids.count(package.partno) != 0:
                packids.remove(package.partno)
            else:
                repeated += '{}, '.format(package.partno)
            volume_t += float(package.width) * float(package.height) * float(package.depth)

        for package in b.unfitted_packages:
            print(package.partno)
        uld_desc_lines = []
        uld_desc_lines.append('space utilization: {}%'.format(round(volume_t / float(volume) * 100, 2)))
        uld_desc_lines.append('residual volume: {}'.format(float(volume) - volume_t))
        uld_desc_lines.append('gravity distribution: {}'.format(b.gravity))
        print('Space Used: {}%'.format(round(volume_t / float(volume) * 100, 2)))
        print('Unused Volume: ', float(volume) - volume_t)
        print("Mass Distribution: ", b.gravity)
        print("***************************************************")
    return uld_desc_lines
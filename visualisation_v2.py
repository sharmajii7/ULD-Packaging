from py3dbp import Packer, Bin, Item, Painter

def visualisation(ulds, packages, packids):
    # Initialize the packer
    packer = Packer()

    # Add ULDs (bins) to the packer
    for uld in ulds:
        packer.addBin(Bin(partno=uld['id'], WHD=(uld['length'], uld['width'], uld['height']),
                          max_weight=uld['weightlimit'], corner=0, put_type=1))

    # Add packages (items) to the packer
    for package in packages:
        if(package['type'] == "Priority"):
            packer.addItem(Item(partno=package['id'], name=package['id'], typeof='cube', 
                            WHD=(package['length'], package['width'], package['height']),
                            weight=package['weight'], level=1, loadbear=100, updown=True, color='olive'))
        else:
            packer.addItem(Item(partno=package['id'], name=package['id'], typeof='cube', 
                            WHD=(package['length'], package['width'], package['height']),
                            weight=package['weight'], level=1, loadbear=100, updown=True, color='pink'))

    # Calculate packing 
    packer.pack(
        bigger_first=True,
        distribute_items=True,
        fix_point=True,
        check_stable=True,
        support_surface_ratio=0.6,
        number_of_decimals=0
    )

    lines = []

    repeated = ''
    for b in packer.bins:
        print(b.partno)
        volume = b.width * b.height * b.depth

        volume_t = 0
        for item in b.items:
            line = ""
            if packids.count(item.partno) != 0:
                packids.remove(item.partno)
            else:
                repeated += '{}, '.format(item.partno)
            originpos = item.position
            rotationtype = item.rotation_type
            line = str(item.partno) + "," + str(b.partno) + ","
            line += str(originpos[0]) + "," + str(originpos[1]) + "," + str(originpos[2]) + ","
            if(rotationtype == 0):
                line += str(originpos[0] + item.width) + "," + str(originpos[1] + item.height) + "," + str(originpos[2] + item.depth) + "\n"
            elif(rotationtype == 1):
                line += str(originpos[0] + item.height) + "," + str(originpos[1] + item.width) + "," + str(originpos[2] + item.depth) + "\n"
            elif(rotationtype == 2):
                line += str(originpos[0] + item.height) + "," + str(originpos[1] + item.depth) + "," + str(originpos[2] + item.width) + "\n"
            elif(rotationtype == 3):
                line += str(originpos[0] + item.depth) + "," + str(originpos[1] + item.height) + "," + str(originpos[2] + item.width) + "\n"
            elif(rotationtype == 4):
                line += str(originpos[0] + item.depth) + "," + str(originpos[1] + item.width) + "," + str(originpos[2] + item.height) + "\n"
            else:
                line += str(originpos[0] + item.width) + "," + str(originpos[1] + item.depth) + "," + str(originpos[2] + item.height) + "\n"
                
            lines.append(line)
            volume_t += float(item.width) * float(item.height) * float(item.depth)

        volume_f = 0
        for item in b.unfitted_items:
            print(item.partno)
            volume_f += float(item.width) * float(item.height) * float(item.depth)

        print('space utilization: {}%'.format(round(volume_t / float(volume) * 100, 2)))
        print('residual volume: ', float(volume) - volume_t)
        print('unpack item volume: ', volume_f)
        print("gravity distribution: ", b.gravity)
        print("***************************************************")

        painter = Painter(b)
        fig = painter.plotBoxAndItems(
            title=b.partno,
            alpha=0.8,
            write_num=True,
            fontsize=10
        )
        fig.show()
        
    return lines

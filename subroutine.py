from py3dbp import Packer, Bin, Item

def subroutine(ulds, packages, packids):
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

    # print("Initial items: ")
    # items = ""
    # for p in packids:
    #     items += '{}, '.format(p)
    # print(items)

    repeated = ''
    # print result
    for b in packer.bins:
        print(b.partno)
        volume = b.width * b.height * b.depth
        # print(":::::::::::", b.string())

        # print("FITTED ITEMS:")
        volume_t = 0
        volume_f = 0
        # unfitted_name = ''
        for item in b.items:
            if(packids.count(item.partno) != 0):
                packids.remove(item.partno)
            else:
                repeated += '{}, '.format(item.partno)
            # print("partno : ",item.partno)
            # print("color : ",item.color)
            # print("position : ",item.position)
            # print("rotation type : ",item.rotation_type)
            # print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
            # print("volume : ",float(item.width) * float(item.height) * float(item.depth))
            # print("weight : ",float(item.weight))
            volume_t += float(item.width) * float(item.height) * float(item.depth)
            # print("***************************************************")
        # print("***************************************************")
        # print("UNFITTED ITEMS:")
        for item in b.unfitted_items:
            # print("partno : ",item.partno)
            # print("color : ",item.color)
            # print("W*H*D : ",str(item.width) +'*'+ str(item.height) +'*'+ str(item.depth))
            # print("volume : ",float(item.width) * float(item.height) * float(item.depth))
            # print("weight : ",float(item.weight))
            volume_f += float(item.width) * float(item.height) * float(item.depth)
            # unfitted_name += '{},'.format(item.partno)
            # print("***************************************************")
        # print("***************************************************")
        print('space utilization: {}%'.format(round(volume_t / float(volume) * 100 ,2)))
        print('residual volumn: ', float(volume) - volume_t )
        # print('unpack item: ',unfitted_name)
        print('unpack item volumn: ',volume_f)
        print("gravity distribution: ",b.gravity)
        print("***************************************************")


    print("Number of unpacked items: ")
    unpacked = ''
    for p in packids:
        unpacked += '{}, '.format(p)
    print(len(packids))
    # print(unpacked)
    print("Repeated packing: ", repeated)
    return len(packids)

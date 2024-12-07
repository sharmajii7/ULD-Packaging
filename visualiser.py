from Subroutine import Assigner, ULD, Package, Plotter
import streamlit as st
def visualiser(ulds, packages, packids,s_s_a_r=0.6):
    # Initialize the packer
    packer = Assigner()

    # Add ULDs (ULDs) to the packer
    for uld in ulds:
        packer.addULD(ULD(partno=uld['id'], WHD=(uld['length'], uld['width'], uld['height']),
                          max_weight=uld['weightlimit']))

    # Add packages (packages) to the packer
    for package in packages:
        if(package['type'] == "Priority"):
            packer.addPackage(Package(partno=package['id'], name=package['id'], 
                            WHD=(package['length'], package['width'], package['height']),
                            weight=package['weight'], loadbear=100, updown=True, color='olive', type="Priority"))
        else:
            packer.addPackage(Package(partno=package['id'], name=package['id'], 
                            WHD=(package['length'], package['width'], package['height']),
                            weight=package['weight'], loadbear=100, updown=True, color='pink', type="Economy"))

    # Calculate packing 
    packer.pack(
        fix_point=True,
        check_stable=True,
        support_surface_ratio=s_s_a_r
    )
    
    # for i in packer.packages:
    #     print(i, end=", ", flush=True)
    # print("")

    lines = []
    x = None
    repeated = ''
    for b in packer.ULDs:
        print(b.partno)
        volume = b.width * b.height * b.depth

        volume_t = 0
        for package in b.packages:
            line = ""
            if packids.count(package.partno) != 0:
                packids.remove(package.partno)
            else:
                repeated += '{}, '.format(package.partno)
            originpos = package.position
            rotationtype = package.rotation_type
            line = str(package.partno) + "," + str(b.partno) + ","
            line += str(originpos[0]) + "," + str(originpos[1]) + "," + str(originpos[2]) + ","
            if(rotationtype == 0):
                line += str(originpos[0] + package.width) + "," + str(originpos[1] + package.height) + "," + str(originpos[2] + package.depth) + "\n"
            elif(rotationtype == 1):
                line += str(originpos[0] + package.height) + "," + str(originpos[1] + package.width) + "," + str(originpos[2] + package.depth) + "\n"
            elif(rotationtype == 2):
                line += str(originpos[0] + package.height) + "," + str(originpos[1] + package.depth) + "," + str(originpos[2] + package.width) + "\n"
            elif(rotationtype == 3):
                line += str(originpos[0] + package.depth) + "," + str(originpos[1] + package.height) + "," + str(originpos[2] + package.width) + "\n"
            elif(rotationtype == 4):
                line += str(originpos[0] + package.depth) + "," + str(originpos[1] + package.width) + "," + str(originpos[2] + package.height) + "\n"
            else:
                line += str(originpos[0] + package.width) + "," + str(originpos[1] + package.depth) + "," + str(originpos[2] + package.height) + "\n"
                
            lines.append(line)
            volume_t += float(package.width) * float(package.height) * float(package.depth)
        
        for package in b.unfitted_packages:
            print(package.partno)

        print('space utilization: {}%'.format(round(volume_t / float(volume) * 100, 2)))
        print('residual volume: ', float(volume) - volume_t)
        print("gravity distribution: ", b.gravity)
        uld_desc_lines = []
        uld_desc_lines.append('space utilization: {}%'.format(round(volume_t / float(volume) * 100, 2)))
        uld_desc_lines.append('residual volume: {}'.format(float(volume) - volume_t))
        uld_desc_lines.append('gravity distribution: {}'.format(b.gravity))
        print("***************************************************")


        painter = Plotter(b)
        fig = painter.plotBoxAndPackages(
            title=b.partno,
            alpha=1,
            write_num=True,
            fontsize=10
        )
        # fig.show()
        st.pyplot(fig)
        # if(len(list_)>=1):
            # list_[len(list_)-1].empty()
        for line in uld_desc_lines:
            st.write(line)
    return lines,fig

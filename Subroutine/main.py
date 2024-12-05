from .auxiliaryMethods import intersect, set2Decimal, RotationType, Axis
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.art3d as art3d
import random
from matplotlib.lines import Line2D
import copy

class Package:
    
    def __init__(self, partno, name, WHD, weight, loadbear, updown, color, type="Economy"):
        ''' '''
        self.partno = partno
        self.name = name
        self.width = WHD[0]
        self.height = WHD[1]
        self.depth = WHD[2]
        self.weight = weight
        self.loadbear = loadbear
        self.updown = updown
        self.color = color
        self.rotation_type = 0
        self.position = [0, 0, 0]
        self.number_of_decimals = 0
        self.type = type


    def formatNumbers(self, number_of_decimals):
        ''' '''
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.weight = set2Decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals


    def getVolume(self):
        ''' '''
        return set2Decimal(self.width * self.height * self.depth, self.number_of_decimals)


    def getDimension(self):
        ''' rotation type '''
        if self.rotation_type == RotationType.RT_WHD:
            return [self.width, self.height, self.depth]
        elif self.rotation_type == RotationType.RT_HWD:
            return [self.height, self.width, self.depth]
        elif self.rotation_type == RotationType.RT_HDW:
            return [self.height, self.depth, self.width]
        elif self.rotation_type == RotationType.RT_DHW:
            return [self.depth, self.height, self.width]
        elif self.rotation_type == RotationType.RT_DWH:
            return [self.depth, self.width, self.height]
        elif self.rotation_type == RotationType.RT_WDH:
            return [self.width, self.depth, self.height]
        return []



class ULD:

    def __init__(self, partno, WHD, max_weight):
        ''' '''
        self.partno = partno
        self.width = WHD[0]
        self.height = WHD[1]
        self.depth = WHD[2]
        self.max_weight = max_weight
        self.packages = []
        self.fit_packages = np.array([[0,WHD[0],0,WHD[1],0,0]])
        self.unfitted_packages = []
        self.number_of_decimals = 0
        self.fix_point = False
        self.check_stable = False
        self.support_surface_ratio = 0
        self.gravity = []


    def formatNumbers(self, number_of_decimals):
        ''' '''
        self.width = set2Decimal(self.width, number_of_decimals)
        self.height = set2Decimal(self.height, number_of_decimals)
        self.depth = set2Decimal(self.depth, number_of_decimals)
        self.max_weight = set2Decimal(self.max_weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals


    def getVolume(self):
        ''' '''
        return set2Decimal(
            self.width * self.height * self.depth, self.number_of_decimals
        )


    def getTotalWeight(self):
        '''Calculate the total weight of all packages and return it formatted to a specified number of decimal places.'''
        
        # Initialize total weight to zero.
        total_weight = 0

        # Iterate over all packages to accumulate their weights.
        for package in self.packages:
            total_weight += package.weight

        # Format the total weight to the specified number of decimal places.
        return set2Decimal(total_weight, self.number_of_decimals)



    def putPackage(self, package, pivot):
        ''' put package in ULD '''
        fit = False
        valid_package_position = package.position
        package.position = pivot
        rotate = RotationType.ALL if package.updown == True else RotationType.Notupdown
        for i in range(0, len(rotate)):
            package.rotation_type = i
            dimension = package.getDimension()
            # rotatate
            if (
                self.width < pivot[0] + dimension[0] or
                self.height < pivot[1] + dimension[1] or
                self.depth < pivot[2] + dimension[2]
            ):
                continue

            fit = True

            for current_package_in_ULD in self.packages:
                if intersect(current_package_in_ULD, package):
                    fit = False
                    break

            if fit:
                # cal total weight
                if self.getTotalWeight() + package.weight > self.max_weight:
                    fit = False
                    return fit
                
                # fix point float prob
                if self.fix_point == True :
                        
                    [w,h,d] = dimension
                    [x,y,z] = [float(pivot[0]),float(pivot[1]),float(pivot[2])]

                    for i in range(3):
                        # fix height
                        y = self.checkHeight([x,x+float(w),y,y+float(h),z,z+float(d)])
                        # fix width
                        x = self.checkWidth([x,x+float(w),y,y+float(h),z,z+float(d)])
                        # fix depth
                        z = self.checkDepth([x,x+float(w),y,y+float(h),z,z+float(d)])

                    # check stability on package 
                    # rule : 
                    # 1. Define a support ratio, if the ratio below the support surface does not exceed this ratio, compare the second rule.
                    # 2. If there is no support under any vertices of the bottom of the package, then fit = False.
                    if self.check_stable == True :
                        # Cal the surface area of ​​package.
                        package_area_lower = int(dimension[0] * dimension[1])
                        # Cal the surface area of ​​the underlying support.
                        support_area_upper = 0
                        for i in self.fit_packages:
                            # Verify that the lower support surface area is greater than the upper support surface area * support_surface_ratio.
                            if z == i[5]:
                                area = len(set([ j for j in range(int(x),int(x+int(w)))]) & set([ j for j in range(int(i[0]),int(i[1]))])) * \
                                len(set([ j for j in range(int(y),int(y+int(h)))]) & set([ j for j in range(int(i[2]),int(i[3]))]))
                                support_area_upper += area

                        # If not , get four vertices of the bottom of the package.
                        if support_area_upper / package_area_lower < self.support_surface_ratio :
                            four_vertices = [[x,y],[x+float(w),y],[x,y+float(h)],[x+float(w),y+float(h)]]
                            #  If any vertices is not supported, fit = False.
                            c = [False,False,False,False]
                            for i in self.fit_packages:
                                if z == i[5]:
                                    for jdx,j in enumerate(four_vertices) :
                                        if (i[0] <= j[0] <= i[1]) and (i[2] <= j[1] <= i[3]) :
                                            c[jdx] = True
                            if False in c:
                                package.position = valid_package_position
                                fit = False
                                return fit
                        
                    self.fit_packages = np.append(self.fit_packages,np.array([[x,x+float(w),y,y+float(h),z,z+float(d)]]),axis=0)
                    package.position = [set2Decimal(x),set2Decimal(y),set2Decimal(z)]

                if fit :
                    self.packages.append(copy.deepcopy(package))

            else :
                package.position = valid_package_position

            return fit

        else :
            package.position = valid_package_position

        return fit


    def checkDepth(self, unfix_point):
        '''Fix package position on the z-axis to avoid overlap with already placed packages.'''
        
        # Initialize z range (min and max) for checking placement.
        z_ranges = [[0, 0], [float(self.depth), float(self.depth)]]

        # Iterate through already placed packages.
        for j in self.fit_packages:
            # Create x and y sets for the current package and the new package (unfix_point).
            x_bottom = set(range(int(j[0]), int(j[1])))
            x_top = set(range(int(unfix_point[0]), int(unfix_point[1])))
            y_bottom = set(range(int(j[2]), int(j[3])))
            y_top = set(range(int(unfix_point[2]), int(unfix_point[3])))

            # Check if there is an overlap in both x and y dimensions.
            if len(x_bottom & x_top) != 0 and len(y_bottom & y_top) != 0:
                # Add z range of the current package to the list for sorting later.
                z_ranges.append([float(j[4]), float(j[5])])

        # Calculate the available depth for the new package.
        top_depth = unfix_point[5] - unfix_point[4]

        # Sort the z ranges by the end of the z range.
        z_ranges = sorted(z_ranges, key=lambda z_range: z_range[1])

        # Iterate through sorted z ranges to check if there's enough space for the new package.
        for j in range(len(z_ranges) - 1):
            # If the gap between two consecutive packages is large enough, return the position.
            if z_ranges[j + 1][0] - z_ranges[j][1] >= top_depth:
                return z_ranges[j][1]

        # If no gap is found, return the starting z position of the new package.
        return unfix_point[4]



    def checkWidth(self, unfix_point):
        '''Fix package position on the x-axis to avoid overlap with already placed packages.'''
        
        # Initialize the x range (min and max) for checking placement.
        x_ranges = [[0, 0], [float(self.width), float(self.width)]]

        # Iterate through already placed packages.
        for j in self.fit_packages:
            # Create z and y sets for the current package and the new package (unfix_point).
            z_bottom = set(range(int(j[4]), int(j[5])))
            z_top = set(range(int(unfix_point[4]), int(unfix_point[5])))
            y_bottom = set(range(int(j[2]), int(j[3])))
            y_top = set(range(int(unfix_point[2]), int(unfix_point[3])))

            # Check if there is an overlap in both z and y dimensions.
            if len(z_bottom & z_top) != 0 and len(y_bottom & y_top) != 0:
                # Add x range of the current package to the list for sorting later.
                x_ranges.append([float(j[0]), float(j[1])])

        # Calculate the available width for the new package.
        top_width = unfix_point[1] - unfix_point[0]

        # Sort the x ranges by the end of the x range.
        x_ranges = sorted(x_ranges, key=lambda x_range: x_range[1])

        # Iterate through sorted x ranges to check if there's enough space for the new package.
        for j in range(len(x_ranges) - 1):
            # If the gap between two consecutive packages is large enough, return the position.
            if x_ranges[j + 1][0] - x_ranges[j][1] >= top_width:
                return x_ranges[j][1]

        # If no gap is found, return the starting x position of the new package.
        return unfix_point[0]

    

    def checkHeight(self, unfix_point):
        '''Fix package position on the y-axis to avoid overlap with already placed packages.'''

        # Initialize y range (min and max) for checking placement.
        y_ranges = [[0, 0], [float(self.height), float(self.height)]]

        # Iterate through already placed packages.
        for j in self.fit_packages:
            # Create x and z sets for the current package and the new package (unfix_point).
            x_bottom = set(range(int(j[0]), int(j[1])))
            x_top = set(range(int(unfix_point[0]), int(unfix_point[1])))
            z_bottom = set(range(int(j[4]), int(j[5])))
            z_top = set(range(int(unfix_point[4]), int(unfix_point[5])))

            # Check if there is an overlap in the x and z dimensions.
            if len(x_bottom & x_top) != 0 and len(z_bottom & z_top) != 0:
                # Add y range of the current package to the list for sorting later.
                y_ranges.append([float(j[2]), float(j[3])])

        # Calculate the available height for the new package.
        top_height = unfix_point[3] - unfix_point[2]

        # Sort the y_ranges by the end of the y range.
        y_ranges = sorted(y_ranges, key=lambda y_range: y_range[1])

        # Iterate through sorted y ranges to check if there's enough space for the new package.
        for j in range(len(y_ranges) - 1):
            # If the gap between two consecutive packages is large enough, return the top position.
            if y_ranges[j + 1][0] - y_ranges[j][1] >= top_height:
                return y_ranges[j][1]

        # If no gap is found, return the starting y position of the new package.
        return unfix_point[2]



class Assigner:

    def __init__(self):
        ''' '''
        self.ULDs = []
        self.packages = []


    def addULD(self, ULD):
        ''' '''
        return self.ULDs.append(ULD)


    def addPackage(self, package):
        ''' '''
        return self.packages.append(package)


    def pack2ULD(self, ULD, package, fix_point, check_stable, support_surface_ratio):
        ''' Pack package to ULD '''
        fitted = False
        ULD.fix_point = fix_point
        ULD.check_stable = check_stable
        ULD.support_surface_ratio = support_surface_ratio

        # If the ULD is empty, directly try placing the package
        if not ULD.packages:
            response = ULD.putPackage(package, package.position)
            if not response:
                ULD.unfitted_packages.append(package)
            return

        # Try to place the package in all possible positions by iterating over the axes
        for axis in range(3):
            for ib in ULD.packages:
                w, h, d = ib.getDimension()

                # Determine the pivot position based on the axis
                if axis == Axis.WIDTH:
                    pivot = [ib.position[0] + w, ib.position[1], ib.position[2]]
                elif axis == Axis.HEIGHT:
                    pivot = [ib.position[0], ib.position[1] + h, ib.position[2]]
                elif axis == Axis.DEPTH:
                    pivot = [ib.position[0], ib.position[1], ib.position[2] + d]

                # Try to place the package at the new pivot position
                if ULD.putPackage(package, pivot):
                    fitted = True
                    break

            if fitted:
                break

        # If the package could not be placed, add it to unfitted packages
        if not fitted:
            ULD.unfitted_packages.append(package)



    def putOrder(self):
        '''Arrange the order of packages'''
        for i in self.ULDs:
            # Sort packages by position in all three dimensions (x, y, z)
            i.packages.sort(key=lambda package: (package.position[1], package.position[2], package.position[0]))
        return



    def gravityCenter(self, ULD):
        """Calculate the deviation of cargo gravity distribution across the ULD.

        Parameters:
        ULD : object
            The ULD object containing the packages to be processed.
        
        Returns:
        list
            The gravity distribution percentages for the four areas of the ULD.
        """
        w, h = int(ULD.width), int(ULD.height)

        # Define the four areas of the ULD as lists of sets
        areas = [
            [set(range(0, w // 2 + 1)), set(range(0, h // 2 + 1)), 0],
            [set(range(w // 2 + 1, w + 1)), set(range(0, h // 2 + 1)), 0],
            [set(range(0, w // 2 + 1)), set(range(h // 2 + 1, h + 1)), 0],
            [set(range(w // 2 + 1, w + 1)), set(range(h // 2 + 1, h + 1)), 0]
        ]

        # Process each package in the ULD
        for package in ULD.packages:
            x_st, y_st = int(package.position[0]), int(package.position[1])
            if package.rotation_type == 0:
                x_ed, y_ed = int(package.position[0] + package.width), int(package.position[1] + package.height)
            elif package.rotation_type == 1:
                x_ed, y_ed = int(package.position[0] + package.height), int(package.position[1] + package.width)
            elif package.rotation_type == 2:
                x_ed, y_ed = int(package.position[0] + package.height), int(package.position[1] + package.depth)
            elif package.rotation_type == 3:
                x_ed, y_ed = int(package.position[0] + package.depth), int(package.position[1] + package.height)
            elif package.rotation_type == 4:
                x_ed, y_ed = int(package.position[0] + package.depth), int(package.position[1] + package.width)
            elif package.rotation_type == 5:
                x_ed, y_ed = int(package.position[0] + package.width), int(package.position[1] + package.depth)

            # Define the x and y ranges for the current package
            x_set, y_set = set(range(x_st, int(x_ed) + 1)), set(range(y_st, int(y_ed) + 1))

            # Calculate the gravity distribution across the four areas
            for idx, area in enumerate(areas):
                area_x, area_y = area[0], area[1]  # Extract the sets for x and y ranges
                if x_set.issubset(area_x) and y_set.issubset(area_y):
                    area[2] += int(package.weight)
                    break
                elif x_set.issubset(area_x) and not y_set.issubset(area_y) and len(y_set & area_y) != 0:
                    y_weight = len(y_set & area_y) / (y_ed - y_st) * int(package.weight)
                    area[2] += y_weight
                    areas[idx - 2 if idx >= 2 else idx + 2][2] += (int(package.weight) - y_weight)
                    break
                elif not x_set.issubset(area_x) and y_set.issubset(area_y) and len(x_set & area_x) != 0:
                    x_weight = len(x_set & area_x) / (x_ed - x_st) * int(package.weight)
                    area[2] += x_weight
                    areas[idx - 2 if idx >= 2 else idx + 2][2] += (int(package.weight) - x_weight)
                    break
                elif not x_set.issubset(area_x) and not y_set.issubset(area_y) and len(y_set & area_y) != 0 and len(x_set & area_x) != 0:
                    total_area = (y_ed - y_st) * (x_ed - x_st)
                    y_part = len(y_set & area_y)
                    y_2 = (y_ed - y_st) - y_part
                    x_part = len(x_set & area_x)
                    x_2 = (x_ed - x_st) - x_part
                    area[2] += x_part * y_part / total_area * int(package.weight)
                    areas[1][2] += x_2 * y_part / total_area * int(package.weight)
                    areas[2][2] += x_part * y_2 / total_area * int(package.weight)
                    areas[3][2] += x_2 * y_2 / total_area * int(package.weight)
                    break

        # Calculate the gravity distribution percentages for each area
        total_weight = sum(area[2] for area in areas)
        if total_weight == 0:
            return [0, 0, 0, 0]

        return [round(area[2] / total_weight * 100, 2) for area in areas]




    def pack(self, fix_point=True, check_stable=True, support_surface_ratio=0.6, number_of_decimals=0):
        """ Main packing function for packing packages into ULDs.

        Parameters:
        fix_point : bool, optional
            Whether to fix the point during the packing process (default is True).
        check_stable : bool, optional
            Whether to check the stability of the packing (default is True).
        support_surface_ratio : float, optional
            Ratio of the support surface, affecting package fitting (default is 0.6).
        number_of_decimals : int, optional
            Number of decimals to format the numbers (default is 0).
        """
        # Format numbers for ULDs and packages
        for ULD in self.ULDs:
            ULD.formatNumbers(number_of_decimals)
        
        for package in self.packages:
            package.formatNumbers(number_of_decimals)

        # Sort ULDs by volume in descending order
        self.ULDs.sort(key=lambda ULD: ULD.getVolume(), reverse=True)

        # Sort packages first by volume, then by load-bearing capacity
        self.packages.sort(key=lambda package: package.getVolume(), reverse=True)
        self.packages.sort(key=lambda package: package.loadbear, reverse=True)

        # Pack packages into ULDs
        for idx, ULD in enumerate(self.ULDs):
            for package in self.packages:
                self.pack2ULD(ULD, package, fix_point, check_stable, support_surface_ratio)
                
                # If there are still unfitted packages, stop the packing process
                if len(ULD.unfitted_packages) != 0:
                    return

            # Update the gravity center of the ULD after packing
            self.ULDs[idx].gravity = self.gravityCenter(ULD)

            # Remove packed packages from the available list
            for bpackage in ULD.packages:
                partno = bpackage.partno
                for package in self.packages:
                    if package.partno == partno:
                        self.packages.remove(package)
                        break

        # Arrange the order of packages
        self.putOrder()




class Plotter:

    def __init__(self,ULDs):
        ''' '''
        self.packages = ULDs.packages
        self.width = ULDs.width
        self.height = ULDs.height
        self.depth = ULDs.depth


    def _plotCube(self, ax, x, y, z, dx, dy, dz, color='red', mode=2, linewidth=1, text="", fontsize=15, alpha=0.5):
        """ Auxiliary function to plot a cube. Code adapted from a web source. """
        
        xx = [x, x, x + dx, x + dx, x]
        yy = [y, y + dy, y + dy, y, y]
        
        kwargs = {'alpha': 1, 'color': color, 'linewidth': linewidth}
        
        if mode == 1:
            # Drawing edges of the cube
            ax.plot3D(xx, yy, [z] * 5, **kwargs)
            ax.plot3D(xx, yy, [z + dz] * 5, **kwargs)
            ax.plot3D([x, x], [y, y], [z, z + dz], **kwargs)
            ax.plot3D([x, x], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y + dy, y + dy], [z, z + dz], **kwargs)
            ax.plot3D([x + dx, x + dx], [y, y], [z, z + dz], **kwargs)
        else:
            # Plotting the faces of the cube using rectangles
            p = Rectangle((x, y), dx, dy, fc=color, ec='black', alpha=alpha)
            p2 = Rectangle((x, y), dx, dy, fc=color, ec='black', alpha=alpha)
            p3 = Rectangle((y, z), dy, dz, fc=color, ec='black', alpha=alpha)
            p4 = Rectangle((y, z), dy, dz, fc=color, ec='black', alpha=alpha)
            p5 = Rectangle((x, z), dx, dz, fc=color, ec='black', alpha=alpha)
            p6 = Rectangle((x, z), dx, dz, fc=color, ec='black', alpha=alpha)
            
            # Adding the patches to the plot
            ax.add_patch(p)
            ax.add_patch(p2)
            ax.add_patch(p3)
            ax.add_patch(p4)
            ax.add_patch(p5)
            ax.add_patch(p6)
            
            # Adding text label if provided
            if text:
                ax.text(
                    (x + dx / 2), (y + dy / 2), (z + dz / 2), str(text),
                    color='black', fontsize=fontsize, ha='center', va='center'
                )
            
            # Converting 2D patches to 3D
            art3d.pathpatch_2d_to_3d(p, z=z, zdir="z")
            art3d.pathpatch_2d_to_3d(p2, z=z + dz, zdir="z")
            art3d.pathpatch_2d_to_3d(p3, z=x, zdir="x")
            art3d.pathpatch_2d_to_3d(p4, z=x + dx, zdir="x")
            art3d.pathpatch_2d_to_3d(p5, z=y, zdir="y")
            art3d.pathpatch_2d_to_3d(p6, z=y + dy, zdir="y")

    def plotBoxAndPackages(self, title="", alpha=0.2, write_num=False, fontsize=10):
        """ Plots the ULD and the packages it contains with random colors. """
        axGlob = plt.axes(projection='3d')
        
        # Plot ULD (Unit Load Device)
        self._plotCube(
            axGlob, 0, 0, 0, float(self.width), float(self.height), float(self.depth),
            color='black', mode=1, linewidth=2, text=""
        )

        # Create a legend list to track colors for the packages
        legend_entries_priority = []
        legend_entries_economy = []
        
        # Plot each package with a random color and add it to the legend
        incpri = 0.2
        inceco = 0.2
        counter = 0
        for package in self.packages:
            x, y, z = package.position
            w, h, d = package.getDimension()
            # Generate a random color for each package
            if(package.type == "Priority"):
                red = 0
                green = incpri
                blue = 0
                incpri += 0.05
                if(incpri > 1):
                    incpri = 0.225
                color = (red, green, blue)
            else:
                red = inceco
                green = 0 
                blue = 0
                inceco += 0.05
                if(inceco > 1):
                    inceco = 0.225
                color = (red, green, blue)
            text = package.partno if write_num else ""
            
            self._plotCube(
                axGlob, float(x), float(y), float(z), float(w), float(h), float(d),
                color=color, mode=2, text=text, fontsize=fontsize, alpha=alpha
            )
            
            # Add the package's color to the legend
            if(package.type == "Priority"):
                legend_entries_priority.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=str(package.partno)))
            else:
                legend_entries_economy.append(Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=str(package.partno)))
            
            counter += 1

        # Set plot title and adjust axes
        plt.title(title)
        self.setAxesEqual(axGlob)
        
        fig = plt.gcf()  # Get the current figure
        fig.set_size_inches(8, 6)
        
        # Add the legend
        first_legend = axGlob.legend(handles=legend_entries_priority, loc='upper center', fontsize=10, ncol=2, bbox_to_anchor=(-0.15, 1.15), borderaxespad=0.5, labelspacing=1.2, title='Priority Packages')
        second_legend = axGlob.legend(handles=legend_entries_economy, loc='upper center', fontsize=10, ncol=2, bbox_to_anchor=(1.10, 1.15), borderaxespad=0.5, labelspacing=1.2, title='Economy Packages')
        
        axGlob.add_artist(first_legend)
        axGlob.add_artist(second_legend)
        # Remove the background color and the box around the plot
        axGlob.set_facecolor('white')  # Set the axes background to white (or 'none' for transparent)

        # Remove the grid
        axGlob.grid(False)

        # Remove the axis markers
        axGlob.set_xticks([])  # Remove x-axis ticks
        axGlob.set_yticks([])  # Remove y-axis ticks
        axGlob.set_zticks([])  # Remove z-axis ticks

        # Remove the axis lines (box)
        axGlob.xaxis.pane.fill = False  # Hide x-axis background (pane)
        axGlob.yaxis.pane.fill = False  # Hide y-axis background (pane)
        axGlob.zaxis.pane.fill = False  # Hide z-axis background (pane)

        # Hide axis lines (the box around the plot)
        axGlob.xaxis.line.set_color('none')  # Remove x-axis line
        axGlob.yaxis.line.set_color('none')  # Remove y-axis line
        axGlob.zaxis.line.set_color('none')  # Remove z-axis line
        
        return plt



    def setAxesEqual(self, ax):
        """ Adjusts the axes of a 3D plot to have equal scale, ensuring that 
        spheres appear as spheres and cubes as cubes, addressing limitations 
        with ax.set_aspect('equal') and ax.axis('equal') in 3D plots.

        Parameters:
        ax : matplotlib axis
            The 3D axis object (e.g., output from plt.gca()).
        """
        # Get axis limits for x, y, and z
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        # Calculate ranges and middle points for each axis
        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        # Define the plot radius as half of the maximum range
        plot_radius = 0.4 * max(x_range, y_range, z_range)

        # Set equal limits for all axes, centered around the middle points
        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])



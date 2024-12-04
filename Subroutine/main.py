from .auxiliaryMethods import intersect, set2Decimal, RotationType, Axis
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.art3d as art3d
import copy

class Package:
    
    def __init__(self, partno, name, WHD, weight, loadbear, updown, color):
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
        ''' '''
        total_weight = 0

        for package in self.packages:
            total_weight += package.weight

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
                            if z == i[5]  :
                                area = len(set([ j for j in range(int(x),int(x+int(w)))]) & set([ j for j in range(int(i[0]),int(i[1]))])) * \
                                len(set([ j for j in range(int(y),int(y+int(h)))]) & set([ j for j in range(int(i[2]),int(i[3]))]))
                                support_area_upper += area

                        # If not , get four vertices of the bottom of the package.
                        if support_area_upper / package_area_lower < self.support_surface_ratio :
                            four_vertices = [[x,y],[x+float(w),y],[x,y+float(h)],[x+float(w),y+float(h)]]
                            #  If any vertices is not supported, fit = False.
                            c = [False,False,False,False]
                            for i in self.fit_packages:
                                if z == i[5] :
                                    for jdx,j in enumerate(four_vertices) :
                                        if (i[0] <= j[0] <= i[1]) and (i[2] <= j[1] <= i[3]) :
                                            c[jdx] = True
                            if False in c :
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
        ''' fix package position z '''
        z_ = [[0,0],[float(self.depth),float(self.depth)]]
        for j in self.fit_packages:
            # creat x set
            x_bottom = set([i for i in range(int(j[0]),int(j[1]))])
            x_top = set([i for i in range(int(unfix_point[0]),int(unfix_point[1]))])
            # creat y set
            y_bottom = set([i for i in range(int(j[2]),int(j[3]))])
            y_top = set([i for i in range(int(unfix_point[2]),int(unfix_point[3]))])
            # find intersection on x set and y set.
            if len(x_bottom & x_top) != 0 and len(y_bottom & y_top) != 0 :
                z_.append([float(j[4]),float(j[5])])
        top_depth = unfix_point[5] - unfix_point[4]
        # find diff set on z_.
        z_ = sorted(z_, key = lambda z_ : z_[1])
        for j in range(len(z_)-1):
            if z_[j+1][0] -z_[j][1] >= top_depth:
                return z_[j][1]
        return unfix_point[4]


    def checkWidth(self, unfix_point):
        ''' fix package position x ''' 
        x_ = [[0,0],[float(self.width),float(self.width)]]
        for j in self.fit_packages:
            # creat z set
            z_bottom = set([i for i in range(int(j[4]),int(j[5]))])
            z_top = set([i for i in range(int(unfix_point[4]),int(unfix_point[5]))])
            # creat y set
            y_bottom = set([i for i in range(int(j[2]),int(j[3]))])
            y_top = set([i for i in range(int(unfix_point[2]),int(unfix_point[3]))])
            # find intersection on z set and y set.
            if len(z_bottom & z_top) != 0 and len(y_bottom & y_top) != 0 :
                x_.append([float(j[0]),float(j[1])])
        top_width = unfix_point[1] - unfix_point[0]
        # find diff set on x_bottom and x_top.
        x_ = sorted(x_,key = lambda x_ : x_[1])
        for j in range(len(x_)-1):
            if x_[j+1][0] -x_[j][1] >= top_width:
                return x_[j][1]
        return unfix_point[0]
    

    def checkHeight(self, unfix_point):
        '''fix package position y '''
        y_ = [[0,0],[float(self.height),float(self.height)]]
        for j in self.fit_packages:
            # creat x set
            x_bottom = set([i for i in range(int(j[0]),int(j[1]))])
            x_top = set([i for i in range(int(unfix_point[0]),int(unfix_point[1]))])
            # creat z set
            z_bottom = set([i for i in range(int(j[4]),int(j[5]))])
            z_top = set([i for i in range(int(unfix_point[4]),int(unfix_point[5]))])
            # find intersection on x set and z set.
            if len(x_bottom & x_top) != 0 and len(z_bottom & z_top) != 0 :
                y_.append([float(j[2]),float(j[3])])
        top_height = unfix_point[3] - unfix_point[2]
        # find diff set on y_bottom and y_top.
        y_ = sorted(y_,key = lambda y_ : y_[1])
        for j in range(len(y_)-1):
            if y_[j+1][0] - y_[j][1] >= top_height:
                return y_[j][1]

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


    def pack2ULD(self, ULD, package,fix_point,check_stable,support_surface_ratio):
        ''' pack package to ULD '''
        fitted = False
        ULD.fix_point = fix_point
        ULD.check_stable = check_stable
        ULD.support_surface_ratio = support_surface_ratio

        if not ULD.packages:
            response = ULD.putPackage(package, package.position)
            if not response:
                ULD.unfitted_packages.append(package)
                return
            return

        for axis in range(0, 3):
            packages_in_ULD = ULD.packages
            for ib in packages_in_ULD:
                pivot = [0, 0, 0]
                w, h, d = ib.getDimension()
                if axis == Axis.WIDTH:
                    pivot = [ib.position[0] + w,ib.position[1],ib.position[2]]
                elif axis == Axis.HEIGHT:
                    pivot = [ib.position[0],ib.position[1] + h,ib.position[2]]
                elif axis == Axis.DEPTH:
                    pivot = [ib.position[0],ib.position[1],ib.position[2] + d]
                    
                if ULD.putPackage(package, pivot):
                    fitted = True
                    break
            if fitted:
                break
        if not fitted:
            ULD.unfitted_packages.append(package)
            return


    def putOrder(self):
        '''Arrange the order of packages '''
        for i in self.ULDs:
            i.packages.sort(key=lambda package: package.position[1], reverse=False)
            i.packages.sort(key=lambda package: package.position[2], reverse=False)
            i.packages.sort(key=lambda package: package.position[0], reverse=False)
        return


    def gravityCenter(self,ULD):
        ''' 
        Deviation Of Cargo gravity distribution
        ''' 
        w = int(ULD.width)
        h = int(ULD.height)

        area1 = [set(range(0,w//2+1)),set(range(0,h//2+1)),0]
        area2 = [set(range(w//2+1,w+1)),set(range(0,h//2+1)),0]
        area3 = [set(range(0,w//2+1)),set(range(h//2+1,h+1)),0]
        area4 = [set(range(w//2+1,w+1)),set(range(h//2+1,h+1)),0]
        area = [area1,area2,area3,area4]

        for i in ULD.packages:
            x_st = int(i.position[0])
            y_st = int(i.position[1])
            if i.rotation_type == 0:
                x_ed = int(i.position[0] + i.width)
                y_ed = int(i.position[1] + i.height)
            elif i.rotation_type == 1:
                x_ed = int(i.position[0] + i.height)
                y_ed = int(i.position[1] + i.width)
            elif i.rotation_type == 2:
                x_ed = int(i.position[0] + i.height)
                y_ed = int(i.position[1] + i.depth)
            elif i.rotation_type == 3:
                x_ed = int(i.position[0] + i.depth)
                y_ed = int(i.position[1] + i.height)
            elif i.rotation_type == 4:
                x_ed = int(i.position[0] + i.depth)
                y_ed = int(i.position[1] + i.width)
            elif i.rotation_type == 5:
                x_ed = int(i.position[0] + i.width)
                y_ed = int(i.position[1] + i.depth)

            x_set = set(range(x_st,int(x_ed)+1))
            y_set = set(range(y_st,y_ed+1))

            # cal gravity distribution
            for j in range(len(area)):
                if x_set.issubset(area[j][0]) and y_set.issubset(area[j][1]) : 
                    area[j][2] += int(i.weight)
                    break
                # include x and !include y
                elif x_set.issubset(area[j][0]) == True and y_set.issubset(area[j][1]) == False and len(y_set & area[j][1]) != 0 : 
                    y = len(y_set & area[j][1]) / (y_ed - y_st) * int(i.weight)
                    area[j][2] += y
                    if j >= 2 :
                        area[j-2][2] += (int(i.weight) - x)
                    else :
                        area[j+2][2] += (int(i.weight) - y)
                    break
                # include y and !include x
                elif x_set.issubset(area[j][0]) == False and y_set.issubset(area[j][1]) == True and len(x_set & area[j][0]) != 0 : 
                    x = len(x_set & area[j][0]) / (x_ed - x_st) * int(i.weight)
                    area[j][2] += x
                    if j >= 2 :
                        area[j-2][2] += (int(i.weight) - x)
                    else :
                        area[j+2][2] += (int(i.weight) - x)
                    break
                # !include x and !include y
                elif x_set.issubset(area[j][0])== False and y_set.issubset(area[j][1]) == False and len(y_set & area[j][1]) != 0  and len(x_set & area[j][0]) != 0 :
                    all = (y_ed - y_st) * (x_ed - x_st)
                    y = len(y_set & area[0][1])
                    y_2 = y_ed - y_st - y
                    x = len(x_set & area[0][0])
                    x_2 = x_ed - x_st - x
                    area[0][2] += x * y / all * int(i.weight)
                    area[1][2] += x_2 * y / all * int(i.weight)
                    area[2][2] += x * y_2 / all * int(i.weight)
                    area[3][2] += x_2 * y_2 / all * int(i.weight)
                    break
            
        r = [area[0][2],area[1][2],area[2][2],area[3][2]]
        result = []
        for i in r :
            if sum(r) == 0:
                result.append(0)  # Append 0 if the sum is zero to avoid division by zero
            else:
                result.append(round(i / sum(r) * 100, 2))
        return result


    def pack(self,fix_point=True,check_stable=True,support_surface_ratio=0.6,number_of_decimals=0):
        '''pack master func '''
        # set decimals
        for ULD in self.ULDs:
            ULD.formatNumbers(number_of_decimals)

        for package in self.packages:
            package.formatNumbers(number_of_decimals)
        # ULD : sorted by volumn
        self.ULDs.sort(key=lambda ULD: ULD.getVolume(), reverse=True)
        # Package : sorted by volumn -> sorted by loadbear
        self.packages.sort(key=lambda package: package.getVolume(), reverse=True)
        self.packages.sort(key=lambda package: package.loadbear, reverse=True)

        for idx,ULD in enumerate(self.ULDs):
            # pack package to ULD
            for package in self.packages:
                self.pack2ULD(ULD, package, fix_point, check_stable, support_surface_ratio)
                if(len(ULD.unfitted_packages) != 0):
                    return
            
            # Deviation Of Cargo Gravity Center 
            self.ULDs[idx].gravity = self.gravityCenter(ULD)
            
            for bpackage in ULD.packages:
                no = bpackage.partno
                for package in self.packages :
                    if package.partno == no :
                        self.packages.remove(package)
                        break

        # put order of packages
        self.putOrder()



class Plotter:

    def __init__(self,ULDs):
        ''' '''
        self.packages = ULDs.packages
        self.width = ULDs.width
        self.height = ULDs.height
        self.depth = ULDs.depth


    def _plotCube(self, ax, x, y, z, dx, dy, dz, color='red',mode=2,linewidth=1,text="",fontsize=15,alpha=0.5):
        """ Auxiliary function to plot a cube. code taken somewhere from the web.  """
        xx = [x, x, x+dx, x+dx, x]
        yy = [y, y+dy, y+dy, y, y]
        
        kwargs = {'alpha': 1, 'color': color,'linewidth':linewidth }
        if mode == 1 :
            ax.plot3D(xx, yy, [z]*5, **kwargs)
            ax.plot3D(xx, yy, [z+dz]*5, **kwargs)
            ax.plot3D([x, x], [y, y], [z, z+dz], **kwargs)
            ax.plot3D([x, x], [y+dy, y+dy], [z, z+dz], **kwargs)
            ax.plot3D([x+dx, x+dx], [y+dy, y+dy], [z, z+dz], **kwargs)
            ax.plot3D([x+dx, x+dx], [y, y], [z, z+dz], **kwargs)
        else :
            p = Rectangle((x,y),dx,dy,fc=color,ec='black',alpha = alpha)
            p2 = Rectangle((x,y),dx,dy,fc=color,ec='black',alpha = alpha)
            p3 = Rectangle((y,z),dy,dz,fc=color,ec='black',alpha = alpha)
            p4 = Rectangle((y,z),dy,dz,fc=color,ec='black',alpha = alpha)
            p5 = Rectangle((x,z),dx,dz,fc=color,ec='black',alpha = alpha)
            p6 = Rectangle((x,z),dx,dz,fc=color,ec='black',alpha = alpha)
            ax.add_patch(p)
            ax.add_patch(p2)
            ax.add_patch(p3)
            ax.add_patch(p4)
            ax.add_patch(p5)
            ax.add_patch(p6)
            
            if text != "":
                ax.text( (x+ dx/2), (y+ dy/2), (z+ dz/2), str(text),color='black', fontsize=fontsize, ha='center', va='center')

            art3d.pathpatch_2d_to_3d(p, z=z, zdir="z")
            art3d.pathpatch_2d_to_3d(p2, z=z+dz, zdir="z")
            art3d.pathpatch_2d_to_3d(p3, z=x, zdir="x")
            art3d.pathpatch_2d_to_3d(p4, z=x + dx, zdir="x")
            art3d.pathpatch_2d_to_3d(p5, z=y, zdir="y")
            art3d.pathpatch_2d_to_3d(p6, z=y + dy, zdir="y")

    def plotBoxAndPackages(self,title="",alpha=0.2,write_num=False,fontsize=10):
        """ side effective. Plot the ULD and the packages it contains. """
        axGlob = plt.axes(projection='3d')
        
        # plot ULD 
        self._plotCube(axGlob,0, 0, 0, float(self.width), float(self.height), float(self.depth),color='black',mode=1,linewidth=2,text="")

        counter = 0
        # fit rotation type
        for package in self.packages:
            x,y,z = package.position
            [w,h,d] = package.getDimension()
            color = package.color
            text= package.partno if write_num else ""

            self._plotCube(axGlob, float(x), float(y), float(z), float(w),float(h),float(d),color=color,mode=2,text=text,fontsize=fontsize,alpha=alpha)
            
            counter += 1  

        
        plt.title(title)
        self.setAxesEqual(axGlob)
        return plt


    def setAxesEqual(self,ax):
        '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
        cubes as cubes, etc..  This is one possible solution to Matplotlib's
        ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

        Input
        ax: a matplotlib axis, e.g., as output from plt.gca().'''
        x_limits = ax.get_xlim3d()
        y_limits = ax.get_ylim3d()
        z_limits = ax.get_zlim3d()

        x_range = abs(x_limits[1] - x_limits[0])
        x_middle = np.mean(x_limits)
        y_range = abs(y_limits[1] - y_limits[0])
        y_middle = np.mean(y_limits)
        z_range = abs(z_limits[1] - z_limits[0])
        z_middle = np.mean(z_limits)

        # The plot bounding box is a sphere in the sense of the infinity
        # norm, hence I call half the max range the plot radius.
        plot_radius = 0.5 * max([x_range, y_range, z_range])

        ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
        ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
        ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


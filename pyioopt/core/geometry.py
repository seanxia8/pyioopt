from collections.abc import Collection
from abc import ABC, abstractmethod

import numpy as np

class detectorGeometry (Collection, ABC) :
    @abstractmethod
    def __init__(self) :
        pass

    @property
    @abstractmethod
    def pmts(self) :
        pass

class cylindricalDetector(detectorGeometry) :
    @property
    @abstractmethod
    def halfHeight(self) :
        pass

    @property
    @abstractmethod
    def radius(self) :
        pass

    def fillRowColumn(self, axis = 'z') :

        self.mask = [[] for i in range(3)]
        
        coords = ['x', 'y', 'z']
        x = [c for c in coords if c not in axis][0]
        y = [c for c in coords if c not in axis][1]
        
        # Let's assume PMTs are equally spaced and treat barrel, top end-cap and bottom end-cap separately
        # Start with barrel.
        # Find extent of PMT positions in Z:
        pmt_z = self._pmts[self._pmts['location'] == 1][axis]
        pmt_z_sorted = np.sort(pmt_z)
        
        pmtZextent = pmt_z_sorted[-1]-pmt_z_sorted[0]
        pmtZmin = pmt_z_sorted[0]
        
        pmt_min_dz = 1e6
        for i in range(len(pmt_z_sorted)-1) :
            dz = pmt_z_sorted[i+1] - pmt_z_sorted[i]
            if (dz > 1e-5) and (dz < pmt_min_dz):
                pmt_min_dz = dz
        
        pmt_xy = [self._pmts[self._pmts['location'] == 1][i] for i in coords if i not in axis]

        pmtRextent = sum([(abs(max(pmt_x)) + abs(min(pmt_x)))/2. for pmt_x in pmt_xy])/len(pmt_xy)

        pmt_rphi = [ pmtRextent * (np.arctan2(pmt_y, pmt_x)+np.pi) for pmt_x, pmt_y in zip(pmt_xy[0], pmt_xy[1]) ]

        pmt_rphi_sorted = np.sort(pmt_rphi)
        pmt_rphi_min = pmt_rphi_sorted[0]
        pmt_rphi_extent = pmt_rphi_sorted[-1] - pmt_rphi_sorted[0]
        pmt_min_drphi = 1e6
        for i in range(len(pmt_rphi_sorted)-1) :
            drphi = pmt_rphi_sorted[i+1] - pmt_rphi_sorted[i]
            if (drphi > 1e-5) and (drphi < pmt_min_drphi) :
                pmt_min_drphi = drphi
                
        N_Z = pmtZextent/pmt_min_dz + 1
        N_PHI = pmt_rphi_extent/pmt_min_drphi + 1

        # Consistency check. Make sure at most one hit per pixel, if not, round up. From the valid choices pick the one with fewer empty pixels.
        isValid = []
        nEmpty = []
        bestnEmpty = 1e6
        for thisN_Z in [np.floor(N_Z), np.ceil(N_Z)] :
            for thisN_PHI in [np.floor(N_PHI), np.ceil(N_PHI)] :
                arr = np.zeros((int(thisN_PHI), int(thisN_Z)))
                nEmpty.append(int(thisN_PHI*thisN_Z) - len(pmt_z))
                if nEmpty[-1] < 0 :
                    print("NOT ENOUGH PIXELS!")
                    isValid.append(0)
                    continue
                
                for rphi, z in zip (pmt_rphi, pmt_z ) :
                    irphi = int((rphi-pmt_rphi_min)/pmt_min_drphi)
                    iz = int((z-pmtZmin)/pmt_min_dz)
             #       print(rphi,irphi, pmt_rphi_min, pmt_rphi_extent)
                    arr[irphi][iz] += 1
                    if arr[irphi][iz] > 1 :
                        print("DOUBLE OCCUPANCY!")
                        print(rphi, z)
                        print(irphi, iz)
                        isValid.append(0)
                        break
                if len(isValid) == len(nEmpty) :
                    continue
                isValid.append(1)
                if nEmpty[-1] < bestnEmpty :
                    bestnEmpty = nEmpty[-1]
                    N_Z = thisN_Z
                    N_PHI = thisN_PHI
                    self.mask[1] = arr == 1
            
        print(len(pmt_z))        
        print(isValid)
        print(nEmpty)

        print (N_Z, N_PHI)
        print(self.mask[1])

        # Repeat for endcaps
        endcapLoc = [0, 2]
        
        min_EC = [{} for i in range(2)]
        d_EC = [{} for i in range(2)]
        N_EC = [{} for i in range(2)]
        
        pmt_x = {}
        
        for endcap in range(2) :
            for i in [x, y] :
                print("I", i)
                pmt_x[i] = self._pmts[self._pmts['location'] == endcapLoc[endcap]][i]
                pmt_x_sorted = np.sort(pmt_x[i])
        
                pmtXextent = pmt_x_sorted[-1]-pmt_x_sorted[0]
                pmtXmin = pmt_x_sorted[0]

                min_EC[endcap][i] = pmtXmin
                
                d_EC[endcap][i] = 1e6
                
                for j in range(len(pmt_x_sorted)-1) :
                    dx = pmt_x_sorted[j+1] - pmt_x_sorted[j]
                    if (dx > 1e-5) and (dx < d_EC[endcap][i]):
                        d_EC[endcap][i] = dx
                N_EC[endcap][i] = pmtXextent/d_EC[endcap][i] + 1

            print(d_EC)
            print(N_EC)
            # Consistency check. Make sure at most one hit per pixel, if not, round up. From the valid choices pick the one with fewer empty pixels.
            isValid = []
            nEmpty = []
            bestnEmpty = 1e6
            for thisN_X in [np.floor(N_EC[endcap][x]), np.ceil(N_EC[endcap][x])] :
                for thisN_Y in [np.floor(N_EC[endcap][y]), np.ceil(N_EC[endcap][y])] :
                    arr = np.zeros((int(thisN_X), int(thisN_Y)))
                    nEmpty.append(int(thisN_X*thisN_Y) - sum(self._pmts['location'] == endcapLoc[endcap]))

                    if nEmpty[-1] < 0 :
                        print("NOT ENOUGH PIXELS!")
                        isValid.append(0)
                        continue
                    
                    for this_x, this_y in zip(pmt_x[x], pmt_x[y]) :
                        ix = int((this_x-min_EC[endcap][x])/d_EC[endcap][x])
                        iy = int((this_y-min_EC[endcap][y])/d_EC[endcap][y])
                        arr[ix][iy] += 1
                        if arr[ix][iy] > 1 :
                            print("DOUBLE OCCUPANCY!")
                            print(this_x, this_y)
                            print(ix, iy)
                            isValid.append(0)
                            break
                    if len(nEmpty) == len(isValid) :
                        continue
                    isValid.append(1)
                    if nEmpty[-1] < bestnEmpty :
                        bestnEmpty = nEmpty[-1]
                        N_EC[endcap][x] = thisN_X
                        N_EC[endcap][y] = thisN_Y
                        self.mask[endcapLoc[endcap]] = arr == 1                            
            
            print(isValid)
            print(nEmpty)
            print(N_EC[endcap][x], N_EC[endcap][y]) 
            print(self.mask[endcapLoc[endcap]])

        barrel = self._pmts['location'] == 1
        endcaps = [self._pmts['location'] == i for i in endcapLoc]

            
        self._pmts['row'][barrel] = ( (pmtRextent * (np.arctan2(self._pmts[y][barrel], self._pmts[x][barrel]) + np.pi) - pmt_rphi_min)/pmt_min_drphi ).astype(int) 
        self._pmts['column'][barrel] = ((self._pmts[axis][barrel]-pmtZmin)/pmt_min_dz).astype(int)
        print(min_EC)
        print(d_EC)
        for i_endcap, endcap in enumerate(endcaps) :
            self._pmts['row'][endcap] = ((self._pmts[x][endcap]-min_EC[i_endcap][x])/d_EC[i_endcap][x]).astype(int)
            self._pmts['column'][endcap] = ((self._pmts[y][endcap]-min_EC[i_endcap][y])/d_EC[i_endcap][y]).astype(int)

    

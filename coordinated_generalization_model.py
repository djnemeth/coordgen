from gdalconst import *
from math import *
from PyQt4.QtCore import *
from qgis.core import *

import gdal
import ogr
import sys

class GeometryData(object):

    def __init__(self, rowCount, columnCount, resolution, topLeftX, topLeftY):
        self.rowCount = rowCount
        self.columnCount = columnCount
        self.resolution = resolution
        self.topLeftX = topLeftX
        self.topLeftY = topLeftY

class CoordinatedGeneralizationModel(object):

    def filterAndSave(self, dsmFileName, waterFileName, outputFileName):
        (array, geometryData) = self._readDatasetAsArray(dsmFileName)
        (array, geometryData) = self._filter(array, geometryData)

        if waterFileName is not None:
            # array = self._correct(array, geometryData, waterFileName)
            pass # would crash currently

        self._save(array, geometryData, outputFileName)

    def _readDatasetAsArray(self, fileName):
        dataset = gdal.Open(fileName, GA_ReadOnly)
        geometryData = GeometryData(dataset.RasterYSize, dataset.RasterXSize,
            abs(dataset.GetGeoTransform()[1]), dataset.GetGeoTransform()[3],
            dataset.GetGeoTransform()[0])

        return (dataset.ReadAsArray(), geometryData)

    def _save(self, array, geometryData, fileName):
        '''Save array dataset as .asc by Zsuzsanna Ungvari'''
        # Modified input
        cm=geometryData.columnCount
        cn=geometryData.rowCount
        cs=geometryData.resolution
        cx=geometryData.topLeftX
        cy=geometryData.topLeftY
        # End of modification

        fn=open(fileName,'w')
        fn.write('ncols '+str(cm)+'\n'+'nrows '+str(cn)+'\n'+'xllcorner '+str(cy)+'\n'+'yllcorner '+str(cx-cn*cs)+'\n'+'cellsize '+str(cs)+'\n')
        for k in range (0,len(array)):
            for l in range (0,len(array[k])):
                fn.write(str(array[k][l])+' ')
            fn.write('\n')
        fn.close()

    def _filter(self, array, geometryData):
        '''Modified image filtering by Zsuzsanna Ungvari'''
        # Modified input
        cm=geometryData.columnCount
        cn=geometryData.rowCount
        cs=geometryData.resolution
        cx=geometryData.topLeftX
        cy=geometryData.topLeftY
        t=array
        # End of modification

        ujt=[]
        for i in range (4,len(t)-4,+3):
            st=[]
            for j in range(4, len(t[i])-4,+3):
                kisebb=0
                a1=(t[i-4][j-4]+t[i-4][j-3]+t[i-4][j-2]+t[i-3][j-4]+t[i-3][j-3]+t[i-3][j-3]+t[i-2][j-4]+t[i-2][j-3]+t[i-2][j-2])/9
                a2=(t[i-4][j-1]+t[i-4][j]+t[i-4][j+1]+t[i-3][j-1]+t[i-3][j]+t[i-3][j+1]+t[i-2][j-1]+t[i-2][j]+t[i-2][j+1])/9
                a8=(t[i+4][j-1]+t[i+4][j]+t[i+4][j+1]+t[i+3][j-1]+t[i+3][j]+t[i+3][j+1]+t[i+2][j-1]+t[i+2][j]+t[i+2][j+1])/9
                a3=(t[i-4][j+4]+t[i-4][j+3]+t[i-4][j+2]+t[i-3][j+4]+t[i-3][j+3]+t[i-3][j+3]+t[i-2][j+4]+t[i-2][j+3]+t[i-2][j+2])/9
                a9=(t[i+4][j+4]+t[i+4][j+3]+t[i+4][j+2]+t[i+3][j+4]+t[i+3][j+3]+t[i+3][j+3]+t[i+2][j+4]+t[i+2][j+3]+t[i+2][j+2])/9
                a4=(t[i-1][j-4]+t[i-1][j-3]+t[i-1][j-2]+t[i][j-4]+t[i][j-3]+t[i][j-2]+t[i+1][j-4]+t[i+1][j-3]+t[i+1][j-2])/9
                a7=(t[i+4][j+4]+t[i+4][j+3]+t[i+4][j+2]+t[i+3][j+4]+t[i+3][j+3]+t[i+3][j+3]+t[i+2][j+4]+t[i+2][j+3]+t[i+2][j+2])/9
                a6=(t[i-1][j+4]+t[i-1][j+3]+t[i-1][j+2]+t[i][j+4]+t[i][j+3]+t[i][j+2]+t[i+1][j+4]+t[i+1][j+3]+t[i+1][j+2])/9
                a5=(t[i-1][j-1]+t[i-1][j]+t[i-1][j+1]+t[i][j-1]+t[i][j]+t[i][j+1]+t[i+1][j-1]+t[i+1][j]+t[i+1][j+1])/9
                if a5<(a1):
                    kisebb+=1
                if a5<(a2):
                     kisebb+=1
                if a5<(a3):
                     kisebb+=1
                if a5<(a4):
                     kisebb+=1
                if a5<(a6):
                     kisebb+=1
                if a5<(a7):
                     kisebb+=1
                if a5<(a8):
                     kisebb+=1
                if a5<(a9):
                     kisebb+=1

                blokk=[t[i-1][j-1],t[i-1][j],t[i-1][j+1],t[i][j-1],t[i][j],t[i][j+1],t[i+1][j-1],t[i+1][j],t[i+1][j+1]]
                blokk.sort()

                st.append(blokk[kisebb])
            ujt.append(st)

        # Modified output
        return (ujt, GeometryData(-2+cn/3, -2+cm/3, cs*3, cx-3*cs, cy+3*cs))
        # End of modification

    def _correct(self, array, geometryData, waterFileName):
        '''River line correction by Zsuzsanna Ungvari'''
        # Modified input
        cm=geometryData.columnCount
        cn=geometryData.rowCount
        cs=geometryData.resolution
        cx=geometryData.topLeftX
        cy=geometryData.topLeftY
        t = array
        # End of modification

        ujt=t
        c = [[0 for i in range(cn)] for j in range(cm)]

        driver = ogr.GetDriverByName('ESRI Shapefile')
        v=driver.Open(waterFileName,1)
        layer=v.GetLayer()
        vt=[]
        numFeatures=layer.GetFeatureCount()
        for i in range(0,numFeatures):
            feat=layer.GetNextFeature()
            geom=feat.GetGeometryRef()
            if geom.GetGeometryName()=="LINESTRING":
                pNum=geom.GetPointCount()
                ut=[]
                for j in range(0,pNum):
                    line = ogr.Geometry(ogr.wkbLineString)
                    if j==0:
                        y=geom.GetPoints(i)[j][0]
                        x=geom.GetPoints(i)[j][1]
                        o=int(floor((y-cy)/cs))
                        s=int(floor((cx-x)/cs))
                        c[s][o]=1
                        ut.append([y,x,t[s][o]])
                    else:
                        y=geom.GetPoints(i)[j][0]
                        x=geom.GetPoints(i)[j][1]
                        ye=geom.GetPoints(i)[j-1][0]
                        xe=geom.GetPoints(i)[j-1][1]
                        tav=self._distance(xe,ye,x,y)
                        if x!=xe and y!=ye:
                            if tav>cs:
                                resz=ceil(tav/cs)
                                if tav/cs>1:
                                    be=[]
                                    be=self._insertPoint(xe,ye,x,y,resz)
                                    for k in range(0,len(be)):
                                        s=be[k][0]
                                        o=be[k][1]
                                        c[s][o]=1
                                        ut.append([y,x,t[s][o]])


                            o=int(floor((y-cy)/cs))
                            s=int(floor((cx-x)/cs))
                            c[s][o]=1
                            ut.append([y,x,t[s][o]])

                vt.append(ut)
            elif geom.GetGeometryName()=="MULTILINESTRING":
                gNum=geom.GetGeometryCount()
                print(feat.GetField('nev'))
                for j in range(0,gNum):
                    g=geom.GetGeometryRef(j)
                    pNum=g.GetPointCount()
                    ut=[]
                    for k in range(0,pNum):
                        if j==0:
                            y=g.GetPoints(j)[k][0]
                            x=g.GetPoints(j)[k][1]
                            o=int(floor((y-cy)/cs))
                            s=int(floor((cx-x)/cs))
                            c[s][o]=1
                            ut.append([y,x,t[s][o]])
                        else:
                            y=g.GetPoints(j)[k][0]
                            x=g.GetPoints(j)[k][1]
                            ye=g.GetPoints(j)[k-1][0]
                            xe=g.GetPoints(j)[k-1][1]
                            tav=self._distance(xe,ye,x,y)
                            if x!=xe and y!=ye:
                                if tav>cs:
                                    resz=ceil(tav/cs)
                                    if tav/cs>1:
                                        be=[]
                                        be=self._insertPoint(xe,ye,x,y,resz)
                                        for k in range(0,len(be)):
                                            s=be[k][0]
                                            o=be[k][1]
                                            c[s][o]=1
                                            ut.append([y,x,t[s][o]])
                                o=int(floor((y-cy)/cs))
                                s=int(floor((cx-x)/cs))
                                c[s][o]=1
                                ut.append([y,x,t[s][o]])
                    vt.append(ut)
        v.Destroy()

        #----------------------------------------------------------Processing
        for i in range(0,len(vt)-1):
            elso=vt[i][0][2]
            utolso=vt[i][len(vt[i])-1][2]
            if elso>utolso: #The line starts on the hill
                a=1
                b=len(vt[i])-1
                c=+1
                zmin=elso
            else: #The line starts at the outfall
                a=len(vt[i])-2
                b=0
                c=-1
                zmin=utolso
            for j in range(a,b,c):
                y=vt[i][j][0]
                x=vt[i][j][1]
                z=vt[i][j][2]
                s=int(floor((cx-x)/cs))
                o=int(floor((y-cy)/cs))
                if z>zmin:
                    vt[i][j][2]=zmin
                    ujt[s][o]=zmin
                    for k in range (-2,3,+1):
                        for l in range(-1,2,+1):
                            ujt[s+k][o+l]=(t[s+k][o+l]+zmin)/2
                else:
                    zmin=z

        # Modified output
        return ujt
        # End of modification

    def _distance(xe, ye, x, y):
        '''Distance between two 2D points by Zsuzsanna Ungvari'''
        return sqrt((xe - x) ** 2 + (ye - y) ** 2)

    def _insertPoint(xe, ye, x, y, resz):
        '''Insert point by Zsuzsanna Ungvari'''
        be=[]
        t=0
        for i in range(1,resz,+1):
            t=t+1/resz
            xk=(1-t)*xe+t*x
            yk=(1-t)*ye+t*y
            o=floor((yk-cy)/cs)
            s=floor((cx-xk)/cs)
            be.append([s,o])
        return be

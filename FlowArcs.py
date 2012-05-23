# -*- coding: utf-8 -*-
"""
FlowArcs.py by François Goulet is licensed under a Creative Commons
Attribution-ShareAlike 3.0 Unported License.
"""

"""
    >python FlowArcs.py [C:/Path/Shapefile.shp] [curvature index]
    
    The source shapefile must be structured like that:
    id | FromX | FromY | ToX | ToY

    
    The script use the values in the shapefile to create the arcs, not the
    geometry of the points. The order is important because it search for the
    position of the field, not its name.
    
    The curvature index determine the "roundness" of the arcs created. With

    an index of 1, you will have a perfect half circle and the higher the 
    index, the flatter the arcs will be. It depends of your data, but with our
    tests, an index of 10 is usually good.
    
    The output will be in a "Arc" directory, in the same as you source
    shapefile.

"""
from sys import argv
import math as m
import osgeo.ogr
import os, os.path, shutil
import shapely.geometry

###############################################################################
def quadrant(pAx, pAy, pBx, pBy):
    """ Calculate the quadrant in which is a destination point compared to
        the origin.

              Y          
              ^          
              |          
       II     |    I     
              |          
    ---------------------> X
              |          
      III     |    IV    
              |          
    """
###############################################################################

    if (pBx>pAx and pBy>pAy):
        return 1
    elif (pBx<pAx and pBy>pAy):
        return 2
    elif (pBx<pAx and pBy<pAy):
        return 3
    elif (pBx>pAx and pBy<pAy):
        return 4
    else:
        return 0


###############################################################################
def EndOfScript():
    """ Sends back a "End of Script" message. Totally useless, but I was tired
        sometime of debugging and need doing something fun ;) """
###############################################################################

    import random
    i = random.randint(1, 25)
 
    if i == 1:
        return "\n-- So Long, and Thanks for All the Fish!"
    elif i == 2:
        return "\n-- 42."
    elif i == 3:
        return "\n-- DON'T PANIC!"
    elif i == 4:
        return "\n-- Do, or do not. There is no 'try'."
    elif i == 5:
        return "\n-- May the Force be with you."
    elif i == 6:
        return "\n-- Frankly, my dear, I don't give a damn."
    elif i == 7:
        return "\n-- You talkin' to me?"
    elif i == 8:
        return "\n-- I love the smell of napalm in the morning."
    elif i == 9:
        return "\n-- Bond. James Bond."
    elif i == 10:
        return "\n-- Show me the money!"
    elif i == 11:
        return "\n-- You can't handle the truth!"
    elif i == 12:
        return "\n-- Hasta la vista, Baby!"
    elif i == 13:
        return "\n-- I see dead people."
    elif i == 14:
        return "\n-- It's alive! It's alive!"
    elif i == 15:
        return "\n-- You had me at 'hello'."
    elif i == 16:
        return "\n-- Elementary, my dear Watson."
    elif i == 17:
        return "\n-- They're here!"
    elif i == 18:
        return """\n-- Striker: Surely you can't be serious. \
                  \n-- Rumack: I am serious...and don't call me Shirley."""
    elif i == 19:
        return "\n-- Adriaaaaan!"
    elif i == 20:
        return "\n-- My precious."
    elif i == 21:
        return "\n-- It's dangerous business, walking out your front door..."
    elif i == 22:
        return "\n-- One does not simply walk into Mordor."
    elif i == 23:
        return """\n-- One Ring to rule them all, One Ring to find them, \
                  \n-- One Ring to bring them all and in the darkness bind them."""
    elif i == 24:
        return "\n-- Well, I'm back."
    elif i == 25:
        return "\n-- Truth hurts. Maybe not as much as jumping on a bicycle with the seat missing, but it hurts.."
    else:
        return "\n-- Oups!"


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################


script, srcSHP, Curve = argv

""" Curvature index """
idxCurve = int(Curve)

""" Opening and reading the shapefile """
shapefile = osgeo.ogr.Open(srcSHP)
layer = shapefile.GetLayer(0)
spatialRef = layer.GetSpatialRef()

""" Output directory """
outDir = os.path.dirname(srcSHP)+"/Arcs/"

""" It erase any previous arcs created so be careful. I know it prevents 
    creating batches, but we didn't have the need... Maybe for next version """
if os.path.exists(outDir):
    shutil.rmtree(outDir)
os.mkdir(outDir)


driver = osgeo.ogr.GetDriverByName("ESRI Shapefile")
outFile = driver.CreateDataSource(os.path.join(outDir,"arcs.shp"))
outLayer = outFile.CreateLayer("layer", spatialRef)

""" Creating string ID field, just in case...."""
fieldDef = osgeo.ogr.FieldDefn("ID", osgeo.ogr.OFTString)
fieldDef.SetWidth(20)
outLayer.CreateField(fieldDef)

fieldDef = osgeo.ogr.FieldDefn("From_X", osgeo.ogr.OFTReal)
outLayer.CreateField(fieldDef)

fieldDef = osgeo.ogr.FieldDefn("From_Y", osgeo.ogr.OFTReal)
outLayer.CreateField(fieldDef)

fieldDef = osgeo.ogr.FieldDefn("To_X", osgeo.ogr.OFTReal)
outLayer.CreateField(fieldDef)

fieldDef = osgeo.ogr.FieldDefn("To_Y", osgeo.ogr.OFTReal)
outLayer.CreateField(fieldDef)

""" Going through each feature, one by one """
for i in range(layer.GetFeatureCount()):
    feature = layer.GetFeature(i)
    
    """ Origin and destination coordinates (floating points)"""
    pA = [0.000000, 0.000000]
    pB = [0.000000, 0.000000]

    """ Fetch the value of the coordinates """
    pA = [feature.GetField(1),feature.GetField(2)]
    pB = [feature.GetField(3),feature.GetField(4)]
   
    
    """ The quadrant determines if the arcs are drawn clockwise or
        counter-clockwise """
    quad = 9            # Default value, for validationm
    quad = quadrant(pA[0], pA[1], pB[0], pB[1])

    
    """ Mid-point of a straight line, from origin to destination """
    pM = [0.000000,0.000000]
    pM[0]=(pB[0]+pA[0])/2.000000
    pM[1]=(pB[1]+pA[1])/2.000000   

    
    """ Creating a triangle. The arc (part of a circle) will pass by the
        origin, destination and this third point (point C)"""
    L = (m.sqrt(m.pow((pA[0]-pB[0]),2)+m.pow((pA[1]-pB[1]),2)))/2
    l = L/idxCurve     


    pMx = pM[0]      # Easier to read than an index number
    pMy = pM[1]       


    """ Angle AB|Y Axis """
    angleABY = m.degrees(m.atan(m.fabs(pA[0]-pMx)/m.fabs(pA[1]-pMy)))
    if quad == 1:
        angleABY = -angleABY
    if quad == 3:
        angleABY = -angleABY

    
    """ Angle AM|AC """
    angleAMAC = m.degrees(m.atan(l/L))

    
    """ Angle AC|X axis """
    if quad == 1:
        angleACX = 90-m.fabs(angleABY)+m.fabs(angleAMAC)
    if quad == 2:
        angleACX = -(90-m.fabs(angleABY)+m.fabs(angleAMAC))
    if quad == 3:
        angleACX = 90-m.fabs(angleABY)-m.fabs(angleAMAC)
    if quad == 4:
        angleACX = -(90-m.fabs(angleABY)-m.fabs(angleAMAC))

    
    """ Length of the line from ptA to ptC """
    ligneAC = m.sqrt(m.pow(l,2)+m.pow(L,2))


    """ coordinates of ptC(pCx, pCy) """
    pC = [0.000000,0.000000]

    if quad == 1:
        pC[0] = pA[0]+ligneAC*m.cos(m.radians(angleACX))
        pC[1] = pA[1]+ligneAC*m.sin(m.radians(angleACX))
    elif quad == 2:
        pC[0] = pA[0]-ligneAC*m.cos(m.radians(angleACX))
        pC[1] = pA[1]-ligneAC*m.sin(m.radians(angleACX))
    elif quad == 3:
        pC[0] = pA[0]-ligneAC*m.cos(m.radians(angleACX))
        pC[1] = pA[1]-ligneAC*m.sin(m.radians(angleACX))
    elif quad == 4:
        pC[0] = pA[0]+ligneAC*m.cos(m.radians(angleACX))
        pC[1] = pA[1]+ligneAC*m.sin(m.radians(angleACX))
    else:
        print "Problems with the quadrant calculations..."
   
  
    """ Crating a circle from 3 known points
        http://en.wikipedia.org/wiki/Circumscribed_circle#Cartesian_coordinates """
    pAx = pA[0]
    pAy = pA[1]
    pBx = pB[0]
    pBy = pB[1]
    pCx = pC[0]
    pCy = pC[1]
    
    circleX = ((pAx*pAx+pAy*pAy)*(pBy-pCy)+ \
               (pBx*pBx+pBy*pBy)*(pCy-pAy)+ \
               (pCx*pCx+pCy*pCy)*(pAy-pBy))/ \
               (2*(pAx*(pBy-pCy)+pBx*(pCy-pAy)+pCx*(pAy-pBy)))  
    circleY = ((pAx*pAx+pAy*pAy)*(pCx-pBx)+ \
               (pBx*pBx+pBy*pBy)*(pAx-pCx)+ \
               (pCx*pCx+pCy*pCy)*(pBx-pAx))/ \
               (2*(pAx*(pBy-pCy)+pBx*(pCy-pAy)+pCx*(pAy-pBy)))
    
    r = m.sqrt((pAx-circleX)*(pAx-circleX) + (pAy-circleY)*(pAy-circleY))
 


    """ Calculating the total length of arc to create (in degrees) """
    
    """ First calculating the quadrant in which are the origin and destination
        compared to the center of the circle """

    quadA = quadrant(circleX, circleY, pAx, pAy)
    quadB = quadrant(circleX, circleY, pBx, pBy)

    
    oppSideA = pAx - circleX
    adjSideA = pAy - circleY
    angleA = m.degrees(m.atan(oppSideA/adjSideA))

    oppSideB = pBx - circleX
    adjSideB = pBy - circleY
    angleB = m.degrees(m.atan(oppSideB/adjSideB))


    """ We use bearing from the center of the circle to determine the start
        and ending of our arc """
    bearingA = 0.000000
    bearingB = 0.000000
    
    if quadA == 1:
        bearingA = angleA
    elif quadA == 2:
        bearingA = angleA
    elif quadA == 3:
        bearingA = -180+angleA
    else:
        bearingA = 180+angleA


    if quadB == 1:
        bearingB = angleB
    elif quadB == 2:
        bearingB = angleB
    elif quadB == 3:
        bearingB = -180+angleB
    else:
        bearingB = 180+angleB   


    """ Creating an empty line """
    lString = osgeo.ogr.Geometry(osgeo.ogr.wkbLineString)    


    """ Creating clockwise or counter-clockwise arcs """   
    if (quad == 1 or quad==4):       # clockwise
        while bearingA < bearingB:
            adj = r*m.cos(m.radians(bearingA))
            opp = r*m.sin(m.radians(bearingA)) 
                        
            pArcX = circleX+opp
            pArcY = circleY+adj
                      
            lString.AddPoint(pArcX,pArcY)
    
                      
            bearingA = bearingA+1     # Will create 1° segments
    
        lString.AddPoint(pBx,pBy)     # Adding the destination point
    
    else:      # counter-clockwise
        while bearingA > bearingB:
            adj = r*m.cos(m.radians(bearingA))
            opp = r*m.sin(m.radians(bearingA)) 
                      
            pArcX = circleX+opp
            pArcY = circleY+adj
                        
            lString.AddPoint(pArcX,pArcY)
                       
            bearingA = bearingA-1     # Will create 1° segments
    
        lString.AddPoint(pBx,pBy)     # Adding the destination point
    

    """ Adding the information from the source file to the output """
    feat = osgeo.ogr.Feature(outLayer.GetLayerDefn())
    feat.SetGeometry(lString)
    feat.SetField("ID", feature.GetField(0))
    feat.SetField("From_X", pA[0])
    feat.SetField("From_Y", pA[1])
    feat.SetField("To_X", pB[0])
    feat.SetField("To_Y", pB[1])
    outLayer.CreateFeature(feat)

# print stupid message
print EndOfScript()

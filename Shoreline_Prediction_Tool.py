                                                        #################################################
                                                        #                                               #
                                                        #         Shoreline Prediction Model            #
                                                        #                                               #
                                                        #                                               #
                                                        #                    By                         #
                                                        #                                               #
                                                        #                                               #
                                                        #              Stephen Escarzaga                #
                                                        #                                               #
                                                        #                                               #
                                                        #                  12/4/15                      #
                                                        #                                               #
                                                        #################################################
                                                       
# READ ME:                                                                                                   
# This script takes points (intersect points between latest shoreline feature and transects) output from DSAS analysis
# The points feature should be names "Points_simplified" (I landed on this because I ended up reducing the number of points to make a more generalized line)
# The lines feature (transects) should be named "Lines"
# Model Assumes there is an "ITEMID" field in both points and lines features
# ITEMID will be populated from "TransOrder" field in the lines attribute table and populated from the "TransectID" field in the points attribute table
# A field named "CHAINAGE" is assumed in the points attribute table. This is populated from whichever rate statistic you choose to go with and is Double type.
# It is best to view results in a map that doesn't currently have the original points a lines features open in the TOC
# ***** denotes where use input should go, namely what ever year you are trying to project shoreline into.
# THIS MODEL ASSUMES LINEAR ERROSION RATE INTO FUTURE
# FOR VISUALIZATION ONLY


import arcpy, arcpy.mapping, os
from arcpy import env
import arcpy.cartography as CA
env.workspace = r"G:\Geocomputation_Project\Section_C\Model_Shapes"
env.overwriteOutput = True

#Run summary statistics on original point file, LCI90 field to out put mean confidence interval to a table.
#This mean CI value will be used as the buffer distance.
arcpy.Statistics_analysis(in_table="Points_simplified.shp",out_table="G:/Geocomputation_Project/Section_C/Model_Shapes/mean_LCI90",statistics_fields="LCI90 MEAN",case_field="#")
print "averaged LCI 90"

#Use search cursor to return the mean LCI 90 value in that table
SC = arcpy.SearchCursor(r"G:/Geocomputation_Project/Section_C/Model_Shapes/mean_LCI90")
field_name = 'MEAN_LCI90'
for row in SC:
    global buff_dist
    buff_dist = row.getValue(field_name)
print "buffer distance set to average LCI 90 value"

# Set local Variables
in_table = 'Points_simplified.shp'
field_x = 'New_X'
field_y = 'New_Y'
#*********************************************************************************************************************************************
expression = "getXY(!Shape!, !ITEMID!, !CHAINAGE!*40)"
code_block_x = """def getXY (point, id, d2add):
    mxd = arcpy.mapping.MapDocument("G:\Geocomputation_Project\Section_C\Model_Shapes\Geocomputation_Project.mxd")
    lyr=arcpy.mapping.ListLayers(mxd,"LINES")[0]
    q='"ITEMID"=%s%s%s' %(r"'",id,"'")
    with arcpy.da.SearchCursor(lyr,"Shape@",q)as cursor:
        for row in cursor:
            line=row[0];break
    pointPos=line.measureOnLine(point)+d2add
    pNew=line.positionAlongLine(pointPos).firstPoint
    return pNew.X"""
code_block_y = """def getXY (point, id, d2add):
    mxd = arcpy.mapping.MapDocument("G:\Geocomputation_Project\Section_C\Model_Shapes\Geocomputation_Project.mxd")
    lyr=arcpy.mapping.ListLayers(mxd,"LINES")[0]
    q='"ITEMID"=%s%s%s' %(r"'",id,"'")
    with arcpy.da.SearchCursor(lyr,"Shape@",q)as cursor:
        for row in cursor:
            line=row[0];break
    pointPos=line.measureOnLine(point)+d2add
    pNew=line.positionAlongLine(pointPos).firstPoint
    return pNew.Y"""
print "field management variables created"

# Execute AddField for each new X and Y coord
arcpy.AddField_management(in_table, field_x, "Double")
arcpy.AddField_management(in_table, field_y, "Double")
print "new x and y fields created"

# Execute CalculateField to each new X and Y field
arcpy.CalculateField_management(in_table, field_x, expression, "PYTHON_9.3", code_block_x)
arcpy.CalculateField_management(in_table, field_y, expression, "PYTHON_9.3", code_block_y)
print "new x and y fields populated"

# Now export the new xy fields and values just created into a text file
# But first remove "test_fields.txt" if it exists file before writing a new one to avoid file locks
try:
    os.remove('G:\\Geocomputation_Project\\Section_C\\Model_Shapes\\test_fields.txt')
except OSError:
    pass

print "test_fields.txt removed"

# set variables for export to text file
outtext = r'G:\Geocomputation_Project\Section_C\Model_Shapes\test_fields.txt'
fc = "Points_simplified.shp"
cursor = arcpy.SearchCursor(fc)
openfile = open(outtext, 'a')
for row in cursor:
    openfile.write(
        str(row.getValue("ITEMID")) + ' ' +
        str(row.getValue("New_X")) + ' ' +
        str(row.getValue("New_Y")) + '\n'
    )
openfile.close()
print "fields exported to text file"

# Load the xy data from the table created in the last step as an events layer

try:
    # set local variables
    in_Table = "test_fields.txt"
    x_coords = "Field2"
    y_coords = "Field3"
    out_layer = "new_points_layer"
    saved_layer = "new_points.lyr"
    # Set Spatial reference
    print "set spatial reference"
    spRef = arcpy.SpatialReference(26904)
    # Make the xy events layer
    print "make xy event layer"
    arcpy.MakeXYEventLayer_management(in_Table, x_coords, y_coords, out_layer, spRef)
    # save to a layer file
    print "saving to a layer file"
    arcpy.SaveToLayerFile_management(out_layer, saved_layer)
    # copy features to shapefile
    print "copying features to shapefile"
    arcpy.CopyFeatures_management(saved_layer, "new_points.shp")
    
except:
    print arcpy.GetMessages()

# generate a line from the points made in the last step
# set local variables
inFeatures = "new_points.shp"
#*********************************************************************************************************************************************
outFeatures = r"G:\Geocomputation_Project\Section_C\Model_Shapes\Output_Lines\line_simp_40"
sortField = "Field1"
# Execute points to line
arcpy.PointsToLine_management(inFeatures, outFeatures)
print "points-to-line done"

#Run a smoothing tool on that new line feature
env.workspace = r"G:\Geocomputation_Project\Section_C\Model_Shapes\Output_Lines"
#*********************************************************************************************************************************************
CA.SmoothLine("line_simp_40.shp", r"G:\Geocomputation_Project\Section_C\Model_Shapes\Output_Lines\line_simp_smooth_40", "BEZIER_INTERPOLATION")
print "line smoothed"

#now buffer the new line feature with mean LCI 90 value
env.workspace = r"G:/Geocomputation_Project/Section_C/Model_Shapes/Output_Lines"
#********************************************************************************************************************************************************************
arcpy.Buffer_analysis("line_simp_smooth_40.shp", r"G:/Geocomputation_Project/Section_C/Model_Shapes/Output_Lines/line_simp_40_buff", (buff_dist * 40), "Full", "Flat")

#Drop New_X and New_Y fields from original point file for new runs
env.workspace = r"G:\Geocomputation_Project\Section_C\Model_Shapes"
dropFields = ["New_X", "New_Y"]
arcpy.DeleteField_management("Points.shp", dropFields)
print "New_X and New_Y fields deleted from point file"




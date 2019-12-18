**Shoreline Change Prediction Model: Utilizing Simple Outputs and Topologies from Shoreline Change Analysis to Model Future Shoreline Positions using ArcPy Scripting**

*Stephen Escarzaga*

The shoreline prediction model uses direct inputs and outputs from a tool called the Digital Shoreline Analysis System (DSAS version 4.0). The tool is a plugin for ArcMap (version 10.0 - 10.5) and was created by the USGS. As seen in Figure 2, the system inputs require digitized, vector format shorelines from different years or time periods. The tool will then create vector lines call "transects" that orient perpendicular to the digitized shorelines. It is along these transects that the system measures erosion rate. Also in Figure 2, the system will output a series of intersect points indicating where all shorelines interested transects. Finally, DSAS will output erosion rates and error statistics (confidence intervals namely) for each transect feature. Figure 3 shows the ROI with digitized shorelines, transects and intersect points.

In the broadest sense, this model will make new intersect points farther down each transect line to simulate a retreating shoreline with each run of the model. The distance from the 0 time step (2015) to the new modeled intersect points depends on the erosion rate for that particular transect line and the number of years the user inputs into the model. The entities (Table 1) of this model are Lines (transects), points (intersect), and Time (# of years to project to). Properties (Table 1) of these entities are as follows: Erosion rate, buffer distance, topological relationship for lines; XY Coordinates and Topological Relationship for points; and number of years for Time. Topological relationship is the geometric overlapping of the points and lines entities. This relationship was exploited in the script to ensure that points moved along lines that shared the same ID in their attribute tables. Lines 25-44 in Script 1 show where the model utilized "measureOnLine" and "positionAlongLine" commands to place a new XY coordinate along a line with the same ID at a measured distance. It is this topological relationship, individual erosion rate and number of years input to the model that will dictate the new XY coordinates for the modeled shoreline position (Figure 4). As mentioned before, DSAS will output calculated confidence interval values for each calculated erosions rate. This model uses this value as a buffer distance for the final predicted shoreline to symbolize uncertainty. Figure 4 shows "# of years" interacting with this buffer distance as the model is set up to multiply this buffer distance by the number of years the user originally inputs for shoreline prediction. The more years the user models the shoreline into the future, the larger the uncertainty of the shoreline.

This script is run outside of ArcMap, however, the entities it calls for are shapefiles and/or tables readable by ArcMap 10.2.2. The following is a step by step description of the model workflow (a broader workflow is detailed in _Figure 5):_ The script begins by running a statistical analysis on the points feature to extract the mean confidence interval for all points along the section of coast.  An expression is created to add new fields to the points shape file for new X and Y coordinates then populate those fields with new values that represent the modeled shoreline (This is where the user would input the number of years he or she wishes to model the shoreline to). These new XY fields are then written to a text file but not before the script checks for the text file that may be present from previous model runs and then deletes them if it exists. This new XY data is then read and saved as a new point shapefile. A points-to-line tool is then run on these new points creating the new modeled shoreline. Then then that new shoreline feature is buffered with a distance of the mean confidence interval calculated at the beginning of the model. Finally, the script deletes the new X and Y coordinate fields in the original points shapefile to allow for future model iterations. With this set up, there are intermediate features created like the new points shapefile that are continuously overwritten so the user doesn&#39;t need to worry about file locks.

![image](https://github.com/smescarzaga/shoreline_predictor/blob/master/4.JPG)
![image](https://github.com/smescarzaga/shoreline_predictor/blob/master/2.JPG)
![image](https://github.com/smescarzaga/shoreline_predictor/blob/master/11.JPG)

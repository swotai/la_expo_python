# README

This is the repository for the LA Expo line project's python codes.  The main code resides in Main folder (single thread).  Prior attempt at multi-threading did not yield correct results and thus is unused and backed up in General Backup folder.

Paths to datasets are specified in main code (*TestDTA.py*, *MAIN.py*, *MAIN_2p.py*) as the *inSpace* variable.  
Set it to the proper path containing the necessary files from the [*Templates* zip file](https://www.dropbox.com/s/w3nl4zq7dekugb2/Template.7z?dl=0)

## Folders
### Main
* The main code is hosted under "Main".  Some core functions are hosted in separate modules
  * ModBuild: building of network dataset
  * ModSetupWorker: file system manipulation to make scratch folder for calculation
  * ModUpdate: code for updating part of the transit network for looping.  Serves as a code base to be used later
* The file A1.1-GIS_GenTransitMatrix-Single.py is the main code for creating the needed matrix.  Files A2 to A5 are variants for different past scenario requirements, and is now not used.

### CF-FastExpo
* This is a variant of the main code.  This code is created to loop through different counterfactual settings for the Expo line to create the master counterfactual dataset.
* The main file to run is A4-GenCF-Fastexpo-v2.py
* Uses the Update Expo module to update the expo line components

### Prototype
* This is a variant of the main code to calculate needed matrices for the prototype city (sim city).
* The main files are: A1-GenTransitProto.py and A2-GenDriveProto.py
* created the Update Transit module based on ModUpdate code for updating sim city transit network.

### General backup
* Contains various old unused codes for future reference
* Various code base for NetworkX routines (*Test NetworkX*)
* Various code base for igraph routines (*Test iGraph*)

## Questions?

[Email me](mailto:kdt43@cornell.edu).
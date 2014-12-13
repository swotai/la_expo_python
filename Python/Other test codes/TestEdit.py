import arcpy
import os

fc = 'Database Connections/Portland.sde/portland.jgp.schools'
fc = 'D:/Mapping/DriveOnly/DriveOnly_LA-test.gdb'
workspace = os.path.dirname(fc)

print workspace
# Start an edit session. Must provide the worksapce.
edit = arcpy.da.Editor(workspace)
print "start edit session"

# Edit session is started without an undo/redo stack for versioned data
#  (for second argument, use False for unversioned data)
edit.startEditing(False, True)
print "start editing"

# Start an edit operation
edit.startOperation()
print "start operation"


# Stop the edit operation.
edit.stopOperation()
print "stop operation"

# Stop the edit session and save the changes
edit.stopEditing(True)
print "stop editing, save changes"

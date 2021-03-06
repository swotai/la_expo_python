# Name: ModSetupWorker.py
# Description: Copy the base gdb to a new temp worker gdb
#              in order to ensure network build successful
# Requirements: shutil (high level file operation)


def clearOld(pathBase, pathTemp):
	import shutil, sys
	
	try:
		shutil.rmtree(pathTemp)
		print "Removed scratch file"

	except Exception as e:
		tb = sys.exc_info()[2]
		print "Exception in ModSetupWorker"
		print "Line %i" % tb.tb_lineno 
		print "If code break here, likely there's a lock on " 
		print pathTemp
		print "Make sure arcGIS or arcCatalog is closed"
		print e.message
    
	finally:
		shutil.copytree(pathBase, pathTemp, symlinks=False, ignore=None)
		print "Created new scratch file"

def copyFour(pathTemp):
	import shutil, sys
	
	try:
		shutil.rmtree(pathTemp[:(len(pathTemp)-4)] + str(1) + ".gdb")
		shutil.rmtree(pathTemp[:(len(pathTemp)-4)] + str(2) + ".gdb")
		shutil.rmtree(pathTemp[:(len(pathTemp)-4)] + str(3) + ".gdb")
		shutil.rmtree(pathTemp[:(len(pathTemp)-4)] + str(4) + ".gdb")
		print "Removed workers"

	except Exception as e:
		tb = sys.exc_info()[2]
		print "Exception in ModSetupWorker: copyFour"
		print "Line %i" % tb.tb_lineno 
		print "If code break here, likely there's a lock on " 
		print pathTemp
		print "Make sure arcGIS or arcCatalog is closed"
		print e.message
    
	finally:
		shutil.copytree(pathTemp, pathTemp[:(len(pathTemp)-4)] + str(1) + ".gdb", 	symlinks=False, ignore=None)
		shutil.copytree(pathTemp, pathTemp[:(len(pathTemp)-4)] + str(2) + ".gdb", 	symlinks=False, ignore=None)
		shutil.copytree(pathTemp, pathTemp[:(len(pathTemp)-4)] + str(3) + ".gdb", 	symlinks=False, ignore=None)
		shutil.copytree(pathTemp, pathTemp[:(len(pathTemp)-4)] + str(4) + ".gdb", 	symlinks=False, ignore=None)
		print "Created new workers"


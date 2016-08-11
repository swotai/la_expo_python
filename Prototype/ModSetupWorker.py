# Name: ModSetupWorker.py
# Description: Copy the base gdb to a new temp worker gdb
#              in order to ensure network build successful
# Requirements: shutil (high level file operation)


def clearOld(pathBase, pathTemp):
	import shutil, os, traceback, sys

	try:
		shutil.rmtree(pathTemp)
		print "removed temp"

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
		print "Copied new temp"
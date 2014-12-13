# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 15:55:33 2014

@author: Dennis
"""

import multiprocessing
import sys
import time

def exit_error():
    sys.exit(1)

def exit_ok():
    return

def return_value():
    return 1

def raises():
    raise RuntimeError('There was an error!')

def terminated():
    time.sleep(3)

        
        
def return_value1():
    time.sleep(1)
    return 1
def return_value3():
    print "yeah yeah Yeah"
    time.sleep(1)
    print "yeah yeah yeah"
    terminated()
    print "yeah yeah"
    return 
def return_value5():
    time.sleep(1)
    return

def runal():
    jobs = []
#    for f in [exit_error, exit_ok, return_value, raises, terminated]:
    for f in [return_value1, return_value3, return_value5]:
        print 'Starting process for', f.func_name
        j = multiprocessing.Process(target=f, name=f.func_name)
        jobs.append(j)
        j.start()
        
#    jobs[-1].terminate()

    for j in jobs:
        j.join()
        print '%s.exitcode = %s' % (j.name, j.exitcode)
    print jobs
    print "Completed"

def runall():
    j1 = multiprocessing.Process(target=return_value1, name=return_value1.func_name)
    j3 = multiprocessing.Process(target=return_value3, name=return_value3.func_name)
    j5 = multiprocessing.Process(target=return_value5, name=return_value5.func_name)
    print 'Starting process'
    j1.start()
    j3.start()
    j5.start()
#    time.sleep(1)
    for j in [j1, j3, j5]:
        print '%s.exitcode = %s' % (j.name, j.exitcode)
    for j in [j1, j3, j5]:
        j.join()
    for j in [j1, j3, j5]:
        print '%s.exitcode = %s' % (j.name, j.exitcode)
    for j in [j1, j3, j5]:
        j.join()


if __name__ == '__main__':
#    jobs = []
##    for f in [exit_error, exit_ok, return_value, raises, terminated]:
#    for f in [return_value1, return_value3, return_value5]:
#        print 'Starting process for', f.func_name
#        j = multiprocessing.Process(target=f, name=f.func_name)
#        jobs.append(j)
#        j.start()
#        
##    jobs[-1].terminate()
#
#    for j in jobs:
#        j.join()
#        print '%s.exitcode = %s' % (j.name, j.exitcode)
        
    runall()
#    mainjob = multiprocessing.Process(target=runal, name=runall.func_name)
#    mainjob.start()
#    mainjob.join()
#    print '%s.exitcode = %s' % (mainjob.name, mainjob.exitcode)

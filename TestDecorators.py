# -*- coding: utf-8 -*-
"""
Created on Tue Oct 21 18:47:24 2014

@author: Dennis
"""

#def outer(some_func):
#	def inner():
#		print "before some_func"
#		ret = some_func()
#		return ret + 1
#	return inner
#
#def foo():
#	return 1
#
#
#class Coordinate(object):
#	def __init__(self, x, y):
#		self.x = x
#		self.y = y
#	def __repr__(self):
#		return "This is coordinates: " + str(self.__dict__)
#		
#def add(a,b):
#	return Coordinate(a.x + b.x, a.y + b.y)
#
#def sub(a,b):
#	return Coordinate(a.x - b.x, a.y - b.y)
#	
#one = Coordinate(100,200)
#two = Coordinate(300,200)
#three = Coordinate(-100,-100)
#
#def wrapper(func):
#	def checker(a,b):
#		if a.x < 0 or a.y < 0:
#			a=Coordinate(a.x if a.x>0 else 0, a.y if a.y>0 else 0)
#		if b.x < 0 or b.y < 0:
#			b=Coordinate(b.x if b.x>0 else 0, b.y if b.y>0 else 0)
#		ret = func(a,b)
#		if ret.x < 0 or ret.y < 0:
#			ret = Coordinate(ret.x if ret.x>0 else 0, ret.y if ret.y>0 else 0)
#		return ret
#	return checker
#
#@wrapper
#def add1(a,b):
#	return Coordinate(a.x+b.x, a.y+b.y)
#	
#def one(*args):
#	print args
#
#one()
#
#one(1,2,3)
#
#def two(x,y, *args):
#	print x,y,args
#
#two('a','b','c')
#
#def add2(x,y):
#	return x+y
#
#lst = [1,2]
#
#print add2(lst[0], lst[1])
#
#print add2(*lst)
#
#def foo1(**kwargs):
#	print kwargs
#	
#foo1()
#foo1(x=1, y=3)

def logger(func):
	def inner(*args, **kwargs):
		print "Arguments were: args %s, kwargs %s" % (args, kwargs)
		return func(*args, **kwargs)
	return inner
	
@logger
def foo1(x, y=1):
	return x*y
	
@logger
def foo2():
	return 2

foo1(5,3)
foo1(4)
foo1(3, y=4)
foo2()

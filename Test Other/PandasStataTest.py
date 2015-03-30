# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 16:44:56 2015

@author: Dennis
"""
inSpace = "C:/Users/Dennis/Desktop/Test/"

# Import all libraries needed for the tutorial

# General syntax to import specific functions in a library: 
##from (library) import (specific library function)
from pandas import DataFrame, read_csv

# General syntax to import a library but no functions: 
##import (library) as (give the library a nickname/alias)
import matplotlib.pyplot as plt
import pandas as pd #this is how I usually import pandas
import sys #only needed to determine Python version number


print 'Python version ' + sys.version
print 'Pandas version ' + pd.__version__

# The inital set of baby names and bith rates
names = ['Bob','Jessica','Mary','John','Mel']
births = [968, 155, 77, 578, 973]

BabyDataset = zip(names,births)
BabyDataset

df = pd.DataFrame(data=BabyDataset, columns=['Names', 'Births'])
df

birthfile = inSpace+'births1880.csv'
df.to_csv(birthfile, index=False, header=False)

df1 = pd.read_csv(birthfile, header=None)
df1 = pd.read_csv(birthfile, names = ['Names', 'Births'])

import os
os.remove(birthfile)
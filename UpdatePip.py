# -*- coding: utf-8 -*-
"""
Created on Tue Dec 09 20:39:16 2014

@author: Dennis
"""

import pip
from subprocess import call

for dist in pip.get_installed_distributions():
    call("pip install --upgrade " + dist.project_name, shell=True)
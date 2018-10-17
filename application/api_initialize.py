#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 11:02:16 2018

@author: brendan
"""

import os.path as path
import json


def import_json(filename):
    # import_json imports a json file in directory "directory" with file name
    # "filename." directory is a folder within the package directory, while
    # this file is in a different foldler in the pacage directory, so we have
    # to navigate up one level and then back down

    # use path.split twice to get the package directory
    (app_directory, thisname) = path.split(__file__)
    # (package_directory, app_folder) = path.split(app_directory)

    # join the directory and fil
    data_path = path.join(app_directory, filename)
    
    
    with open(data_path) as json_data:
        data = json.load(json_data)

    return data

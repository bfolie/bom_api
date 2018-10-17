#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  9 09:05:37 2018

@author: brendan
"""

from flask import Flask
app = Flask(__name__)

import application.api
import application.api_helper
import application.api_error_handler
import application.api_initialize
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 11:49:29 2018

@author: brendan
"""


class InvalidUsage(Exception):
    """
    Class used to send error information to the clien
    They should know the error status code, and some additional human-readable
    info on why that code appeared
    """

    status_code = 400  # default is 400 (bad request)

    def __init__(self, message, status_code=None):
        # Initialize instance. It contains a message (string)
        # and status code (int)
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            # If user specifies a status code, change from 400
            # to whatever they specified
            self.status_code = status_code

    def to_dict(self):
        # Convert object into a dictionary
        # (which can then be jsonified and output to the user)
        output = dict()
        output['error'] = self.status_code
        output['message'] = self.message
        return output

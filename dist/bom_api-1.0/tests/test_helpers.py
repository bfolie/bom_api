#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 24 18:10:46 2018

@author: brendan
"""

from application import api
from application import api_helper
from application import api_initialize
from application.api_error_handler import InvalidUsage

import pytest


def test_check_part_exists():
    # test_parts is a simple list of parts that is imported at the beginning
    # of each test function. It consists of 4 parts, with id's 1 to 4.
    # parts 1 and 2 are children of part 3.
    # parts 1 and 4 have one attribute each
    test_parts = api_initialize.import_json('test_data.json')
    
    # Part 2 should exist, but part 17 should not
    assert api_helper.check_part_exists(2, test_parts) == True
    assert api_helper.check_part_exists(17, test_parts) == False


def test_get_part():
    # get part 1 and make sure it has the correct values
    test_parts = api_initialize.import_json('test_data.json')
    part = api_helper.get_part(1, test_parts)
    assert part['id'] == 1
    assert part['name'] == 'screw'
    assert part['children'] == []
    assert part['attributes'] == ['thread']
    assert part['children attribute values'] == []
    
    with pytest.raises(InvalidUsage):
        api_helper.get_part(17, test_parts)


def test_get_part_index():
    # Part with id = 2 should correspond to index = 1
    test_parts = api_initialize.import_json('test_data.json')
    assert api_helper.get_part_index(2, test_parts) == 1


def test_new_part_id():
    # Generating a new id should return 5. If we pass an empty list it should
    # return 1
    test_parts = api_initialize.import_json('test_data.json')
    assert api_helper.new_part_id(test_parts) == 5
    assert api_helper.new_part_id([]) == 1

def test_check_loops():
    # Initially there should be no loops. Then attach part 3 to part 1,
    # and it should detect a loop
    test_parts = api_initialize.import_json('test_data.json')
    assert api_helper.check_loops(test_parts) == False
    test_parts_copy = test_parts.copy()
    test_parts_copy[0]['children'] = [3]
    assert api_helper.check_loops(test_parts_copy) == True


def test_add_children():
    # Add part 4 to part 3 and make sure the new values are correct
    test_parts = api_initialize.import_json('test_data.json')
    parent = api_helper.get_part(3, test_parts)
    new_children, new_children_attributes = api_helper.add_children(
            parent, [4], [['green']], test_parts)
    assert new_children == [1, 2, 4]
    assert new_children_attributes == [['8-24'], [], ['green']]


def test_remove_children():
    # remove part 1 from part 3 and make sure the new values are correct
    test_parts = api_initialize.import_json('test_data.json')
    parent = api_helper.get_part(3, test_parts)
    new_children, new_children_attributes = api_helper.remove_children(
            parent, [1])
    assert new_children == [2]
    assert new_children_attributes == [[]]


def test_is_child():
    # Check that part 1 is a child, but part 3 is not
    test_parts = api_initialize.import_json('test_data.json')
    part1 = api_helper.get_part(1, test_parts)
    part3 = api_helper.get_part(3, test_parts)
    assert api_helper.is_child(part1, test_parts) == True
    assert api_helper.is_child(part3, test_parts) == False
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 10:05:07 2018

@author: brendan
"""

from application import api_error_handler 
from application.api_error_handler import InvalidUsage
import operator


def check_part_exists(part_id, parts):
    # check_part_exists returns true or false depending on whether or not
    # there's a part in the parts list with id part_id

    # list of all parts that match id
    parts_list = [part for part in parts if part['id'] == part_id]
    if len(parts_list) == 0:
        return False
    return True


def get_part(part_id, parts):
    # get_part returns part with id part_id

    # list of all parts that match id
    parts_list = [part for part in parts if part['id'] == part_id]
    if len(parts_list) == 0:
        # if part does not exist, raise 404 error
        raise InvalidUsage('This part does not exist', status_code=404)
    return parts_list[0]


def get_part_index(part_id, parts):
    # get_part_index finds the position in the parts list
    # of a part with id part_id
    for index, part in enumerate(parts):  # cycle through parts list
        # if this part has 'id' part_id, then return the current index
        if part['id'] == part_id:
            return index

    return -1  # if part_id wasn't found, return -1


def new_part_id(parts):
    # new_part_id figures out what id number to assign to a new part

    if len(parts) == 0:
        return 1  # if there are no parts, give this one id = 1
    else:
        return parts[-1]['id'] + 1  # else add 1 to the id of the last part


def check_attributes_list(attributes_list):
    # get_attributes_list

    if type(attributes_list) is not list:
        attributes_list = [attributes_list]

    attributes_list_out = []
    for attribute in attributes_list:
        if type(attribute) is not str:
            raise InvalidUsage("Invalid attributes list", status_code=400)
        attributes_list_out.append(attribute)

    return attributes_list_out


def add_children(parent, additions_list, attribute_values_list, parts):
    # add_children takes a part's list of current children and a list of
    # additions and combines them.
    # parent is the part to which children are being added.
    # additions_list is a list of ids for the parts to add.
    # attribute_values_list is a list of attribute lists. The first attribute
    # list corresponds to the first child, the second to the second child,
    # etc. An attribute list can be empty if that child has no attributes.
    # For example, if additions_list = [13, 14, 16] and the part with id 13
    # has no attributes, id 14 has 2 attributes, and id 16 has one attribute,
    # attribute_values_list might look like the following:
    # [[], ['red', 'metal'], ['opaque']]
    # parts is a list of all parts

    # make a copy of the current list of parent's children (for modification)
    new_children = parent['children'].copy()
    new_children_attributes = parent['children attribute values'].copy()

    # Cycle through the list of child_id to add, and
    # check to see if we can actually add each one
    for (child_id, attribute_values) in zip(additions_list,
        attribute_values_list):
        # If there's no part with this id, throw a resource not found error
        if not check_part_exists(child_id, parts):
            raise InvalidUsage("Cannot attach part with id {0}; it does not "
                               "exist".format(str(child_id)), status_code=404)

        # As long as the child_id isn't already in the list
        # and isn't equal to the parent_id, it's ok to proceed
        if not (child_id == parent['id'] or child_id in parent['children']):
            # append child_id to the new list of this parent's children
            child = get_part(child_id, parts)
            if type(attribute_values) is not list:
                attribute_values = [attribute_values]

            if not len(child['attributes']) == len(attribute_values):
                raise InvalidUsage("Child with id {0} has wrong number of att"
                                   "ributes".format(child_id), status_code=400)

            new_children.append(child_id)
            new_children_attributes.append(attribute_values)

    return new_children, new_children_attributes


def remove_children(parent, removal_list):
    # remove_children takes a part's list of current children and
    # removes those in a second list
    # current_list is a list of ids for the current children of this part
    # removal_list is a list of ids to remove

    # make a copy of the current list of parent's children (for modification)
    new_list = parent['children'].copy()
    new_attribute_values = parent['children attribute values'].copy()

    # cycle through the list of child_id to remove,
    # and check to see if it's in current_list
    for child_id in removal_list:
        if child_id in new_list:
            # if child_id is in current_list, remove it and its attributes
            index = new_list.index(child_id)
            new_list.pop(index)
            new_attribute_values.pop(index)
        else:
            # if it's not there, throw a resource not found error
            raise InvalidUsage("Child {0} is not part of this "
                               "assembly".format(str(child_id)),
                               status_code=404)

    return new_list, new_attribute_values


def scrub_part(part_id, parts):
    # scrub_part removes part_id from all assemblies of which it may be a part
    # part_id is the id of the part to be deleted,
    # and parts is the master list of parts
    for part in parts:  # cycle through the parts
        # if part_id is in this part's children, then remove it
        if part_id in part['children']:
            index = part['children'].index(part_id)
            part['children'].pop(index)
            part['children attribute values'].pop(index)

    return


def is_child(test_part, parts):
    # is_child checks to see if a given part is the child in any assemblies
    # test_part is the part to check, and parts is the master list of all parts

    part_id = test_part['id']  # get the id of the test part
    for part in parts:  # cycle through all parts
        # if part_id shows up in the 'children' list of this part, return True
        if part_id in part['children']:
            return True

    # if part_id didn't show up as a child of any part, return False
    return False


def check_loops(parts):
    # check_loops checks to make sure there are no infinite dependency loops
    # in the list of parts (i.e. part A has part B as a child, and part B has
    # part A as a child).
    # Returns True if there are loops, False if there are not

    # list to track which parts have been visited
    visited = [False]*len(parts)
    # list of the recursion stack -- parts that have been visited this cycle
    recursion_stack = [False]*len(parts)

    for index, part in enumerate(parts):  # cycle through the parts list
        # if this part has not been visited yet, check to see if it's on a loop
        if not visited[index]:
            if is_loop(index, parts, visited, recursion_stack):
                return True

    return False


def is_loop(index, parts, visited, recursion_stack):
    # is_loop checks to see if the a specific part (given by index) in the list
    # of parts is on a loop.
    # visited and recursion_stack are lists tracking which parts have been
    # visited ever and which have been visited in the most recent loop

    visited[index] = True
    recursion_stack[index] = True

    # cycle through this part's children
    for child_id in parts[index]['children']:
        # need to convert id's to indices
        child_index = get_part_index(child_id, parts)

        # if child_index >= 0 makes sure there's a valid part with this id.
        # If not we skip it, because it's not the job of this function to make
        # sure that all of the parts exist, it's just checking for loops

        # if this child hasn't been visited (and exists)
        if child_index >= 0 and not visited[child_index]:
            # then check to see if it's part of a loop
            if is_loop(child_index, parts, visited, recursion_stack):
                return True
        # else if this part is on the recursion stack, then we've found a loop
        elif recursion_stack[child_index]:
                return True

    recursion_stack[index] = False  # remove this part from the recursion stack
    return False  # return False -- no loop found here


def get_all_children_id(part_id, parts):
    # get_all_children_id returns a list of the id's of every part that is a
    # child of the part given by part_id, either directly or indirectly
    # It works recursively

    # use part_id to get the part and copy a list of its children
    part = get_part(part_id, parts)
    children = part['children'].copy()

    # base case: if there are no children, return an empty list
    if not children:
        return list()

    # cycle through all of the immediate children (id given by child_id)
    # run get_all_children on child_id, and add the result to children
    # hence children is an ever-expanding list of ALL children
    for child_id in children:
        children = children + get_all_children_id(child_id, parts)

    # to remove duplicates, turn children into a set and then back into a list
    return list(set(children))


def get_routes(app):
    # get_routes returns a list of all routes within the Flask object app
    # Each entry in the dictionary is a route, and it has within it another
    # dictionary containing the endpoint and the available methods

    rules = []  # empty dictionary to hold rules
    for rule in app.url_map.iter_rules():
        # app.url_map.iter_rules() makes an iterable of all the possible rules
        # sort and make a list of the methods (GET, POST, etc.)
        methods = ','.join(sorted(rule.methods))
        # append a tuple with the endpoint
        rules.append((rule.endpoint, methods, str(rule)))

    # sort the rules by str(rule) (or URLs are in alphabetical order)
    sort_by_rule = operator.itemgetter(2)

    routes = {}  # make a dictionary to hold the rules and turn into json
    # iterate through the sorted rule tuples
    for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
        # add a dictionary entry for this rule
        routes[rule] = {'endpoint': endpoint, 'methods': methods}

    return routes


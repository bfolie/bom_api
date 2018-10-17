#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 29 18:08:57 2018

@author: brendan
"""

from flask import Flask, jsonify, request

from application import api_helper
from application import api_initialize
from application.api_error_handler import InvalidUsage

parts = []  # master list of all parts; start as empty list
# import starting parts for testing purposes
parts = api_initialize.import_json('starting_data.json')


from application import app

if __name__ == '__main__':
    app.run(debug=True)


@app.route("/parts", methods=['GET'])
def get_parts():
    # get_parts returns a list of all parts

    if len(parts) == 0:
        # if no parts, raise 404 error
        raise InvalidUsage('No parts exist', status_code=404)
    return jsonify({'parts': parts})  # return json of parts list


@app.route("/parts/<int:part_id>", methods=['GET'])
def get_part(part_id):
    # get_part returns the specific part given by id

    part = api_helper.get_part(part_id, parts)
    return jsonify({'part': part})


@app.route("/parts", methods=['POST'])
def add_part():
    # add_part adds a new part to the master list of parts
    # user past pass a json with the following fields:
    # name: the name of the new part (string)
    # attributes: the attributes that the part has, such as color
    # or material. It is a list (possibly empty) of strings

    if not request.json or 'name' not in request.json:
        # if the command doesn't include a 'name' field, raise 400 error
        raise InvalidUsage('name field missing from request', status_code=400)

    if not isinstance(request.json['name'], str):
        # if the name isn't a string, raise 400 error
        raise InvalidUsage('name field must be a string', status_code=400)

    if 'attributes' not in request.json:
        attributes = []
    else:
        attributes = api_helper.check_attributes_list(
                request.json['attributes'])

    # figure out the id for the new part
    part_id = api_helper.new_part_id(parts)

    new_part = {
            'id': part_id,
            'name': request.json['name'],
            'children': [],
            'children attribute values': [],
            'attributes': attributes
            }  # create dictionary entry for this new part

    parts.append(new_part)  # append new part to master parts list
    return jsonify({'new part': new_part}), 201


@app.route("/parts/<int:parent_id>", methods=['PUT'])
def modify_children(parent_id):
    # modify_children attaches/removes one or more parts to/from a parent part
    # The function below mostly consists of checking for errors, and then the
    # actual addition/removal takes place in helper functions.
    # User mast pass a json with the following fields:
    # action: a string that is either "attach" or "remove"
    # children: a list of the id's of children to attach or remove
    # If children are being attached, there must also be a field
    # "attribute values" which specifies the value of each attribute the
    # children have. It's a list of lists. For example if the children being
    # attached have id's [3, 6, 4] then the first item of "attribute values"
    # is a list of attributes for the part with id 3. If this child with id 3
    # has attributes "color" and "material", then the attribute values list
    # might be ["red", "plastic"]

    parent = api_helper.get_part(parent_id, parts)

    if not request.json:
        # if request is not in json format, error
        raise InvalidUsage('Modification must be in JSON format',
                           status_code=400)

    if 'children' not in request.json:
        # if json request doesn't include a 'children' key, throw an error
        raise InvalidUsage('children field missing from request',
                           status_code=400)

    if 'action' not in request.json:
        # If json request doesn't include an 'action' key, throw an error
        raise InvalidUsage('action field missing from request',
                           status_code=400)

    # Extract list of children to add/remove from json request
    # If the user didn't give the children ids in list form, make it a list
    # Want to allow the case where the user wants to attach/remove a single
    # part, and instead of sending a list of ids just sends the id as an int
    parts_list = request.json['children']
    if type(parts_list) is not list:
        parts_list = [parts_list]

    # call a function to modify the list of children
    # depending on the 'action' keyword
    if request.json['action'] == 'attach':
        # attach children
        # check to make sure there's a list of attribute values, and it
        # is the same length as the list of new children to add
        if 'attribute values' not in request.json:
            raise InvalidUsage('attribute values field missing from request',
                           status_code=400)

        # since attribute values exist, extract from json
        attribute_values = request.json['attribute values']

        # if it's not a list, make it a list
        if type(attribute_values) is not list:
            attribute_values = [attribute_values]
        # if the lengths of the children list and attribute values list
        # don't line up, throw an error
        if not len(attribute_values) == len(parts_list):
            raise InvalidUsage("list of attributes does not match list of "
                               "children to add", status_code=400)

        # now that these checks have been done, can actually add children
        new_children_list, new_children_attributes_list = api_helper.add_children(
                parent, parts_list, attribute_values, parts)
    elif request.json['action'] == 'remove':
        # remove children
        new_children_list, new_children_attributes_list = api_helper.remove_children(
                parent, parts_list)
    else:
        raise InvalidUsage('action field must specify attach or remove',
                           status_code=400)

    # modify the list of children, but first create a copy of the current
    # list, in case we have to revert after checking for loops
    old_children_list = parent['children'].copy()
    parent['children'] = new_children_list

    if api_helper.check_loops(parts):
        # check to see if any loops have been created
        # if so, revert to the old list of children and raise error
        parent['children'] = old_children_list
        raise InvalidUsage("Cannot add parts to assembly, as it creates an "
                           "infinite loop", status_code=409)

    parent['children attribute values'] = new_children_attributes_list
    return jsonify({'assembly': parent})


@app.route("/parts/<int:part_id>", methods=['DELETE'])
def delete_part(part_id):
    # delete_part deletes a part from the parts list and from all assemblies
    # part_id is the id number of the part to be deleted

    # list of all parts that match id
    parts_list = [part for part in parts if part['id'] == part_id]
    if len(parts_list) == 0:
        # if the above list is empty, return 404
        raise InvalidUsage('This part does not exist', status_code=404)

    parts.remove(parts_list[0])  # delete the part itself

    # find all instances where it is part of an assembly, and delete
    api_helper.scrub_part(part_id, parts)

    return jsonify({'result': True})


@app.route("/assemblies", methods=['GET'])
def get_assemblies():
    # get_assemblies returns a list of all assemblies (parts with children)

    if len(parts) == 0:
        # if no parts, return resource not found
        raise InvalidUsage('No parts exist', status_code=404)

    # find all assemblies -- parts for which the list of children is not empty
    assemblies = [part for part in parts if part['children']]
    return jsonify({'assemblies': assemblies})  # return list as json


@app.route("/top-assemblies", methods=['GET'])
def get_top_assemblies():
    # get_top_assemblies returns a list of all top level assemblies
    # (parts that have children and are not themselves children)

    if len(parts) == 0:
        # if no parts, return resource not found
        raise InvalidUsage('No parts exist', status_code=404)

    # find all top assemblies -- parts for which the list of children is not
    # empty, and they are not children of some other part
    top_assemblies = ([part for part in parts if part['children']
                      and not api_helper.is_child(part, parts)])

    return jsonify({'top assemblies': top_assemblies})  # return list as json


@app.route("/subassemblies", methods=['GET'])
def get_subassemblies():
    # get_sub_assemblies returns a list of all subassemblies (parts that have
    # children and are also themselves children of some other part)

    if len(parts) == 0:
        # if no parts, return resource not found
        raise InvalidUsage('No parts exist', status_code=404)

    # find all  subassemblies -- parts for which the list of children is
    # not empty, and they are children of some other part
    subassemblies = [part for part in parts if part['children']
                     and api_helper.is_child(part, parts)]
    return jsonify({'subassemblies': subassemblies})  # return list as json


@app.route("/components", methods=['GET'])
def get_components():
    # get_components returns a list of all components (partsthat do
    # not have children but are themselves children of some other part)

    if len(parts) == 0:
        # if no parts, return resource not found
        raise InvalidUsage('No parts exist', status_code=404)

    # find all  components -- parts for which the list of children is empty,
    # and they are children of some other part
    components = ([part for part in parts if not part['children']
                  and api_helper.is_child(part, parts)])

    return jsonify({'components': components})  # return list as json


@app.route("/orphans", methods=['GET'])
def get_orphans():
    # get_orphans returns a list of all orphans
    # (parts that do not have children and are not children of some other part)

    if len(parts) == 0:
        # if no parts, return resource not found
        raise InvalidUsage('No parts exist', status_code=404)

    # find all  orphans -- parts for which the list of children is empty,
    # and they are not children of some other part
    orphans = ([part for part in parts if not part['children']
                and not api_helper.is_child(part, parts)])

    return jsonify({'orphans': orphans})  # return list as json


@app.route("/parts/<int:part_id>/top-children", methods=['GET'])
def get_top_children(part_id):
    # get_top_children returns all top-level children of a part
    # with id given by part_id

    part = api_helper.get_part(part_id, parts)
    top_children_id = part['children']
    top_children = [api_helper.get_part(top_child_id, parts)
                    for top_child_id in top_children_id]

    return jsonify({'top children': top_children})


@app.route("/parts/<int:part_id>/all-children", methods=['GET'])
def get_all_children(part_id):
    # get_all_children returns all children of a part with id given by part_id
    # It returns all top-level children, the children of those children,
    # etc. all the way down

    children_id = api_helper.get_all_children_id(part_id, parts)
    children = [api_helper.get_part(child_id, parts)
                for child_id in children_id]

    return jsonify({'all children': children})


@app.route("/parts/<int:part_id>/ancestors", methods=['GET'])
def get_ancestors(part_id):
    # get_ancestors returns all assemblies that contain the part with id given
    # by part_id. This includes assemblies which contain part_id directly, but
    # also the assemblies that contain those assemblies, etc. all the way up

    if not api_helper.check_part_exists(part_id, parts):
        # if part does not exist, raise 404 error
        raise InvalidUsage('This part does not exist', status_code=404)

    # loop through test_part in parts, and run api_helper.get_all_children_id()
    # on test_part. If part_id is in the list of children for test_part, then
    # test_part goes on the list of ancestors
    ancestors = [test_part for test_part in parts if part_id
                 in api_helper.get_all_children_id(test_part['id'], parts)]

    return jsonify({'ancestors': ancestors})


@app.route("/", methods=['GET'])
def get_routes():
    # get_routes returns a json dictionary of all routes
    # Each entry in the dictionary is a route, and it has within it another
    # dictionary containing the endpoint and the available methods

    # actual work done by api_helper.get_routes, which returns a list
    # simply turn that list into a json and return
    routes = api_helper.get_routes(app)
    return jsonify({'routes': routes})


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    # handle_invalid_usage raises an instance of the InvalidUsage class

    # turn error into a dictionary and then JSON
    response = jsonify(error.to_dict())
    # set the error status code (e.g. 400, 404, etc.)
    response.status_code = error.status_code
    return response


@app.errorhandler(404)
def page_not_found(error):
    # error handling for a bad route
    response = {'error': 404, 'message': 'Page not found'}
    return jsonify(response)

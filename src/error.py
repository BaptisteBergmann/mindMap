'''
Filename: error.py
Path: ./src/
Created Date: Monday, April 25rd 2022, 10:41:08 am
Author: Baptiste Bergmann
'''

class CustomExeptions(Exception):
    code = 500

class LeafNotFound(CustomExeptions):
    code = 404
    description = 'Leaf not found'

class MapNotFound(CustomExeptions):
    code = 404
    description = 'Map not found'

class PathNotValid(CustomExeptions):
    code = 509
    description = 'The path is not valid'

class LeafExist(CustomExeptions):
    code = 510
    description = 'The leaf already there'
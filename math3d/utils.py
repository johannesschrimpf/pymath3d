'''
Copyright (C) 2011 Morten Lind
mailto: morten@lind.no-ip.org

This file is part of PyMath3D (Math3D for Python).

PyMath3D is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyMath3D is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyMath3D.  If not, see <http://www.gnu.org/licenses/>.
'''
'''
Utility function and definitions library for PyMath3D.
'''

import numpy as np

## Possibly replace by 1000*np.finfo(float).resolution
_eps = 10e-10

## Tuple of types considered sequences 
_seqTypes = (list, tuple, np.ndarray)

def isSequence(s):
    return type(s) in _seqTypes

def isThreeSequence(s):
    return type(s) in _seqTypes and len(s) == 3

## Standard numeric types
_numTypes = [float, int]
## Get numeric types from numpy
for i in np.typeDict:
    if type(i) == type('') and (i.find('int') >= 0 or i.find('float') >= 0):
        _numTypes.append(np.typeDict[i])
        
def isNumType(val):
    return type(val) in _numTypes

def isNumTypes(lst):
    for li in lst:
        if type(li) not in _numTypes:
            return False
    return True

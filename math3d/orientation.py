"""
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
"""
"""
Module implementing the Orientation class. The orientation is
represented internally by an orthogonal 3x3 matrix.
"""

from copy import copy

import numpy as np

import math3d
from math3d.utils import isSequence, isNumTypes, _eps

def isOrientation(o):
    print('Deprecation warning: "isOrientation(o)".'
          + ' Use "type(o) == math3d.Orientation".')
    return type(o) == Orientation

class Orientation(object):
    """ An Orientation is a member of SO(3) which can be used either
    to perform a rotational transformation, or for keeping an
    orientation in 3D."""
    
    class Error(Exception):
        """ Exception class."""
        def __init__(self, message):
            self.message = message
        def __repr__(self):
            return self.__class__ + '.Error :' + self.message

    @classmethod
    def canCreateOn(cls, *args):
        """ Infer whether an Orientation can be constructed on the
        given argument tuple. This is mostly syntactic, down to the
        level of testing whether basic types are numeric. Testing
        whether constraints among the individual basic values are
        violated is not tested."""
        if len(args) == 1:
            arg = args[0]
            if type(arg) in [Orientation, math3d.Quaternion, math3d.Vector]:
                return True
            elif isSequence(arg):
                return cls.canCreateOn(*arg)
            else:
                return False
        elif len(args) == 3:
            for arg in args:
                if not math3d.Vector.canCreateOn(arg):
                    return False
                return True
        elif len(args) == 9:
            return isNumTypes(args)
        else:
            return False

    def __createOnSequence(self, args):
        """ Assuming args to be a sequence, try to create the data of
        an orientation over it."""
        crOK = True
        if type(args) == np.ndarray:
            if args.shape == (3,):
                ## Construct on a rotation vector
                self._data = np.identity(3)
                self.fromRotationVector(args)
            elif args.shape == (3,3):
                ## Take over a copy of the matrix. Warning: No
                ## constraint checks.
                self._data = args.copy()
            else:
                crOK = False
        elif type(args) in (list,tuple):
            if len(args) == 3:
                ## Assume three row vectors of the matrix. Dangerous, no checks.
                self._data=np.array(args)
            elif len(args) == 9:
                ## Assume flat array of three row vectors. Dangerous, no checks.
                oa=np.array(args)
                oa.shape=[3,3]
                self._data = oa
            else:
                crOK = False
        else:
            raise Orientation.Error(
                'Could not create Orientation data on "%s"' % str(args))
                
    def __init__(self, *args):
        """ Create an orientation on another Orientation, a
        Quaternion, three Vectors, 12 numbers, or a 3x3 array. In case
        of 12 numbers, they are perceived as row-major order."""
        if len(args) == 1:
            arg=args[0]
            if type(arg) == Orientation:
                self._data = arg._data.copy()
            elif type(arg) == math3d.Quaternion:
                self._data = arg.toOrientation()._data
            elif type(arg) == math3d.Vector:
                ## Interpret as a rotation vector
                self._data = np.identity(3)
                self.fromRotationVector(arg)
            elif isSequence(arg):
                self.__createOnSequence(arg)
        elif len(args) > 1:
            self.__createOnSequence(args)
        elif len(args) == 0:
            self._data = np.identity(3)

    def __copy__(self):
        """Copy method for creating a copy of this Orientation."""
        o = Orientation()
        o.copy(self)
        return o
    
    def __deepcopy__(self, memo):
        return self.__copy__()
    
    def copy(self, other=None):
        """Copy data from other to self. """
        if other is None:
            return copy(self)
        else:
            self._data[:,:] = other._data.copy()
    
    def __getattr__(self, name):
        if name == 'data':
            return self._data.copy()
        elif name[:3] in ['vec', 'col'] and name[3] in 'XYZ':
            idx = 'XYZ'.find(name[3])
            a = self._data[:,idx]
            if name[:3] == 'vec':
                a = math3d.Vector(a)
            return a
        else:
            raise AttributeError('Attribute "%s" not found in Orientation'%name)
            #raise self.Error, 'Orientation does not have attribute "%s"' % name
        
    def __getitem__(self, indices):
        return self._data.__getitem__(indices)
    
    def __coerce__(self, other):
        if type(other) == Orientation:
            return (self, other)
        else:
            return None
        
    def __eq__(self,other):
        if type(other) == Orientation:
            return np.sum((self._data-other._data)**2) < _eps
        else:
            raise self.Error('Could not compare to non-Orientation!')


    def __setattr__(self, name, val):
        if name == '_data':
            ## This is dangerous, since there is no consistency check.
            self.__dict__['_data']=val
        elif name[:3] in ['vec', 'col'] and name[3] in 'XYZ':
            ## This is dangerous since there is no automatic
            ## re-normalization
            if type(val) == math3d.Vector:
                val = val.data
            if name[3] == 'X':
                self._data[:3,0] = val
            elif name[3] == 'Y':
                self._data[:3,1] = val
            elif name[3] == 'Z':
                self._data[:3,2] = val
        else:
            object.__setattr__(self, name, val)
        
    def fromXY(self, cx, cy):
        """ Reset this orientation to the one that conforms with the
        given x and y directions."""
        if cx * cy > _eps:
            print('warning ... orthogonalizing!')
            #print ('%s %s'%(str(cx),str(cy))
        self.colX = cx.normalized()
        self.colY = cy.normalized()
        self.colZ = cx.cross(cy).normalized()
        ## A last normalization check!
        #if self.colX.dist(self.colY.cross(self.colZ)) > _eps:
        self.colX=self.colY.cross(self.colZ)
        
    def fromXZ(self, cx, cz):
        """ Reset this orientation to the one that conforms with the
        given x and z directions."""
        if cx * cz > _eps:
            print('warning ... orthogonalizing!')
        self.colX = cx.normalized()
        self.colZ = cz.normalized()
        self.colY = cz.cross(cx).normalized()
        ## A last normalization check!
        #if self.colX.dist(self.colY.cross(self.colZ)) > _eps:
        self.colX = self.colY.cross(self.colZ)


    def toRotationVector(self):
        """ Return a rotation vector representing this
        orientation. This is essentially the logarithm of the rotation
        matrix."""
        q = math3d.Quaternion(self)
        return q.toRotationVector()

    def fromRotationVector(self, rotVec):
        """ Set this Orientation to represent the one given in
        'rotVec'."""
        if type(rotVec) == math3d.Vector:
            rotVec = rotVec.data
        angle = np.linalg.norm(rotVec)
        axis = rotVec/angle
        self.fromAxisAngle(axis, angle)

    def toAxisAngle(self):
        """ Return an (axis,angle) pair representing the equivalent
        orientation."""
        q = math3d.Quaternion(self)
        return q.toAxisAngle()

    def fromAxisAngle(self, axis, angle):
        """ Set this orientation to the equivalent to rotation of
        'angle' around 'axis'."""
        if type(axis) == math3d.Vector:
            axis = axis.data
        ## Force normalization
        axis /= np.linalg.norm(axis)
        x = axis[0]
        y = axis[1]
        z = axis[2]
        ct =np.cos(angle)
        st = np.sin(angle)
        self._data[:,:] = np.array([ \
            [ct + (1 - ct) * x**2,
             (1 - ct) * x * y - st *z,
             (1 - ct) * x * z + st * y],
            [(1 - ct) * x * y + st * z,
             ct + (1 - ct) * y**2,
             (1 - ct) * y * z - st * x],
            [(1 - ct) * x * z - st * y,
             (1 - ct) * y * z + st * x,
             ct + (1 - ct) * z**2]])

    def rotX(self, angle):
        """ Replace this orientation by that of a rotation around x."""
        ca = np.cos(angle)
        sa = np.sin(angle)
        self._data[:,:] = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
        #self.fromAxisAngle(math3d.Vector.e0, angle)
        
    def rotY(self, angle):
        """ Replace this orientation by that of a rotation around y."""
        ca=np.cos(angle)
        sa=np.sin(angle)
        self._data[:,:] = np.array([[ca, 0, sa], [0, 1, 0], [-sa, 0, ca]])
        #self.fromAxisAngle(math3d.Vector.e1, angle)
        
    def rotZ(self, angle):
        """ Replace this orientation by that of a rotation around z. """
        ca = np.cos(angle)
        sa = np.sin(angle)
        self._data[:,:] = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
        #self.fromAxisAngle(math3d.Vector.e2,angle)

    def rotateT(self, axis, angle):
        """ In-place rotation of this orientation angle radians in
        axis perceived in the transformed reference system."""
        o = Orientation()
        o.fromAxisAngle(axis, angle)
        self.copy(self * o)
    rotate = rotateT
    
    def rotateB(self, axis, angle):
        """ In-place rotation of this orientation angle radians in
        axis perceived in the base reference system."""
        o = Orientation()
        o.fromAxisAngle(axis, angle)
        self.copy(o * self)

    def rotateXB(self, angle):
        """ In-place rotation of this oriantation by a rotation around
        x axis in the base reference system. (Inefficient!)"""
        self.rotateB(math3d.Vector.e0, angle)
    
    def rotateYB(self, angle):
        """ In-place rotation of this oriantation by a rotation around
        y axis in the base reference system. (Inefficient!)"""
        self.rotateB(math3d.Vector.e1, angle)
    
    def rotateZB(self, angle):
        """ In-place rotation of this oriantation by a rotation around
        z axis in the base reference system. (Inefficient!)"""
        self.rotateB(math3d.Vector.e2, angle)
    
    def rotateXT(self, angle):
        """ In-place rotation of this oriantation by a rotation around
        x axis in the transformed reference system. (Inefficient!)"""
        self.rotateT(math3d.Vector.e0, angle)
    rotateX = rotateXT
    
    def rotateYT(self,angle):
        """ In-place rotation of this oriantation by a rotation around
        y axis in the transformed reference system. (Inefficient!)"""
        self.rotateT(math3d.Vector.e1,angle)
    rotateY = rotateYT
    
    def rotateZT(self, angle):
        """ In-place rotation of this oriantation by a rotation around
        z axis in the transformed reference system. (Inefficient!)"""
        self.rotateT(math3d.Vector.e2, angle)
    rotateZ = rotateZT
    
    def __repr__(self):
        return '<Orientation: \n' + repr(self._data) + '>'

    def __str__(self):
        return self.__repr__()

    def angDist2(self, other):
        """ Return the square of the orientation distance (the angle
        of rotation) to the 'other' orientation."""
        return (self.inverse()*other).toRotationVector().length2()

    def angDist(self, other):
        """ Return the orientation distance (the angle of rotation) to
        the 'other' orientation."""
        return np.sqrt(self.angDist2(other))
    
    def invert(self):
        """ In-place inversion of this orientation."""
        self._data[:,:] = self._data.transpose().copy()

    def inverse(self):
        """ Return an inverse of this orientation as a rotation."""
        o = Orientation(self._data)
        o.invert()
        return o

    def __mul__(self, other):
        if type(other) == Orientation:
            return Orientation(np.dot(self._data, other._data))
        elif type(other) == math3d.Vector:
            return math3d.Vector(np.dot(self._data, other._data))
        elif isSequence(other):
            return list(map(self.__mul__, other))
        
def newOrientFromXY(cx, cy):
    """ Create an orientation conforming with the given 'x' and 'y'
    directions."""
    o = Orientation()
    o.fromXY(cx, cy)
    return o

def newOrientFromXZ(cx, cz):
    """ Create an orientation conforming with the given 'x' and 'z'
    directions."""    
    o = Orientation()
    o.fromXZ(cx, cz)
    return o

def newOrientRotZ(angle):
    """ Create an orientation corresponding to a rotation for 'angle'
    around the z direction."""
    o = Orientation()
    o.rotZ(angle)
    return o

def newOrientRotX(angle):
    """ Create an orientation corresponding to a rotation for 'angle'
    around the x direction."""
    o = Orientation()
    o.rotX(angle)
    return o

def newOrientRotY(angle):
    """ Create an orientation corresponding to a rotation for 'angle'
    around the y direction."""
    o = Orientation()
    o.rotY(angle)
    return o

if __name__ == '__main__':
    o = Orientation()
    r = Orientation()
    o.fromXY(math3d.Vector(1, 1, 0), math3d.Vector(-1, 1, 0))
    r.rotZ(np.pi / 2)
    ro = r * o

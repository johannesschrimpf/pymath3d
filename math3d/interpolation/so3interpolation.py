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
Module implementing the SO(3) interpolator class; Slerp.
"""

from math3d.orientation import Orientation
from math3d.quaternion import Quaternion

class SO3Interpolation(object):
    """ A SLERP interpolator class in SO(3)."""
    
    class Error(Exception):
        """ Exception class."""
        def __init__(self, message):
            self.message = message
        def __repr__(self):
            return self.__class__ + '.Error :' + self.message, None

    def __init__(self, start, end, shortest=True):
        """ Initialise an SO(3) interpolation from orientation 'start'
        to orientation 'end'. If 'shortest' is true, the shortest
        rotation path is chosen, if false, it is indeterminate.""" 
        self._qstart = Quaternion(start) if type(start) == Orientation else start
        self._qend = Quaternion(end) if type(end) == Orientation else end
        self._qstart.normalize()
        self._qend.normalize()
        if shortest and self._qstart.dist(self._qend) > self._qstart.dist(-self._qend):
            self._qend = -self._qend
        self._qstartconj = self._qstart.conjugated().normalized()
        self._qstartconjqend = (self._qstartconj * self._qend).normalized()

    def __call__(self,t):
        return self.quat(t)
    
    def quat(self, time, checkrange=True):
        """ Return the quaternion in the slerp at 'time'; in [0,1]."""
        if checkrange:
            time = float(time)
            if time < 0.0 or time > 1.0:
                raise self.Error('"time" must be number in [0,1]. Was %f' % time) 
        return self._qstart * (self._qstartconjqend) ** time

    def orient(self, time, checkrange=True):
        """ Return the orientation in the slerp at 'time'; in [0,1]. """
        return self.quat(time, checkrange).toOrientation()
    
SLERP = SO3Interpolation
OrientationInterpolation = SO3Interpolation

def _test():
    """ Simple test function."""
    global o, o1, q, q1, osl, qsl
    from math import pi
    o = Orientation()
    o.rotX(pi / 2)
    o1 = Orientation()
    o1.rotZ(pi / 2)
    q = Quaternion(o)
    q1 = Quaternion(o1)
    qsl = SO3Interpolation(q,q1)
    osl = SO3Interpolation(o,o1)

if __name__ == '__main__':
    import readline
    import rlcompleter
    readline.parse_and_bind("tab: complete")


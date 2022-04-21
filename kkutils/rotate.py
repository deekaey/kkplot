
import math
import numpy as numpy
from numpy.linalg import inv as matrix_inverse


def  translation_matrix( _point) :
    T = numpy.array( \
            [ [ 1.0, 0.0, 0.0, -_point[0]], \
              [ 0.0, 1.0, 0.0, -_point[1]], \
              [ 0.0, 0.0, 1.0, -_point[2]], \
              [ 0.0, 0.0, 0.0,  1.0]])
    return  T
def  translation_matrix_inverse( _point) :
    T = translation_matrix( _point)
    return  matrix_inverse( T)

def  rotation_matrix_x( _phi) :
    R = numpy.array( \
            [ [ 1.0, 0.0,              0.0,             0.0], \
              [ 0.0, math.cos( _phi), -math.sin( _phi), 0.0], \
              [ 0.0, math.sin( _phi),  math.cos( _phi), 0.0], \
              [ 0.0, 0.0,              0.0,             1.0]])
    return  R

def  rotation_matrix_y( _phi) :
    R = numpy.array( \
            [ [  math.cos( _phi), 0.0, math.sin( _phi), 0.0], \
              [  0.0,             1.0, 0.0,             0.0], \
              [ -math.sin( _phi), 0.0, math.cos( _phi), 0.0], \
              [  0.0,             0.0, 0.0,             1.0]])
    return  R

def  rotation_matrix_z( _phi) :
    R = numpy.array( \
            [ [ math.cos( _phi), -math.sin( _phi), 0.0, 0.0], \
              [ math.sin( _phi),  math.cos( _phi), 0.0, 0.0], \
              [ 0.0,              0.0,             1.0, 0.0], \
              [ 0.0,              0.0,             0.0, 1.0]])
    return  R

def  degree_to_radians( _phi) :
    return float( _phi) * math.pi / 180.0

def  rotation_matrix( _phi, _p0=(0,0,0), _isdegree=False) :
    rot_matrix = numpy.identity( 4)

    assert( len(_phi) == 3 )
    if _isdegree :
        phi_x, phi_y, phi_z = ( degree_to_radians( _phi[0]),
            degree_to_radians( _phi[1]), degree_to_radians( _phi[2]))
    else :
        phi_x, phi_y, phi_z = _phi

    need_rotate = False
    if abs( phi_x) > 0.0 :
        rot_matrix = rotation_matrix_x( phi_x)
        need_rotate = True
    if abs( phi_y) > 0.0 :
        rot_matrix = numpy.dot( rot_matrix, rotation_matrix_y( phi_y))
        need_rotate = True
    if abs( phi_z) > 0.0 :
        rot_matrix = numpy.dot( rot_matrix, rotation_matrix_z( phi_z))
        need_rotate = True
    if need_rotate :
        tra_matrix = translation_matrix( _p0)
        itra_matrix = translation_matrix_inverse( _p0)
        rot_matrix = numpy.dot( itra_matrix, numpy.dot( rot_matrix, tra_matrix))

    return rot_matrix

def  rotate_point( _point, _rotation_matrix) :
    return numpy.dot( _rotation_matrix,
        numpy.array( [ _point[0], _point[1], _point[2], 1.0]))

def  rotate_points( _points, _rotation_matrix) :
    points = list()
    for point in _points :
        p = rotate_point( point, _rotation_matrix)
        points.append(( p[0], p[1], p[2]))
    return points

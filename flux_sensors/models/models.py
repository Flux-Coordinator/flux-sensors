#!/usr/bin/env python

import time
import datetime


class Position(object):
    """Model class for a 3D position"""

    def __init__(self, x_position, y_position, z_position):
        self.x = x_position
        self.y = y_position
        self.z = z_position

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z


class Reading(object):
    """Model class for a flux reading"""

    def __init__(self, lux_value, position):
        self.luxValue = lux_value
        self.xposition = position.get_x()
        self.yposition = position.get_y()
        self.zposition = position.get_z()

        time_stamp = time.time()
        self.timestamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

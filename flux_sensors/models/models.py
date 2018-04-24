#!/usr/bin/env python

import time
import datetime


class Position(object):
    """Model class for a 3D position"""

    def __init__(self, x_position: float, y_position: float, z_position: float) -> None:
        self.x = x_position
        self.y = y_position
        self.z = z_position

    def get_x(self) -> float:
        return self.x

    def get_y(self) -> float:
        return self.y

    def get_z(self) -> float:
        return self.z


class Reading(object):
    """Model class for a flux reading"""

    def __init__(self, lux_value: float, position: Position) -> None:
        self.luxValue = lux_value
        self.xposition = position.get_x()
        self.yposition = position.get_y()
        self.zposition = position.get_z()

        time_stamp = time.time()
        self.timestamp = datetime.datetime.now().isoformat()

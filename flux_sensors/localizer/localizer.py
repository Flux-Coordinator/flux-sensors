#!/usr/bin/env python

from pypozyx import (POZYX_POS_ALG_UWB_ONLY, POZYX_3D, Coordinates, POZYX_SUCCESS, POZYX_ANCHOR_SEL_AUTO,
                     DeviceCoordinates, PozyxSerial, get_first_pozyx_serial_port, SingleRegister, DeviceList)


class Localizer(object):
    """Interface for Pozyx positioning"""

    def __init__(self, pozyx, anchors=None, dimension=POZYX_3D, height=1000,
                 algorithm=POZYX_POS_ALG_UWB_ONLY, remote_id=None):
        self._pozyx = pozyx
        self._anchors = []
        if anchors is not None:
            self._anchors = anchors
        self._dimension = dimension
        self._height = height
        self._algorithm = algorithm
        self._remote_id = remote_id
        self._is_initialized = False

    def is_initialized(self):
        return self._is_initialized

    def add_anchor(self, anchor_id, coordinates):
        self._is_initialized = False
        self._anchors.append(DeviceCoordinates(anchor_id, 1, coordinates))

    def clear_anchors(self):
        self._is_initialized = False
        del self._anchors[:]

    def get_number_of_anchors(self):
        return len(self._anchors)

    def initialize(self):
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        self.write_anchors_to_pozyx()
        self.check_pozyx_configuration
        self._is_initialized = True

    def write_anchors_to_pozyx(self):
        """Adds the anchors to the Pozyx's device list one for one."""
        status = self._pozyx.clearDevices(self._remote_id)
        for anchor in self._anchors:
            status &= self._pozyx.addDevice(anchor, self._remote_id)
        if len(self._anchors) > 4:
            status &= self._pozyx.setSelectionOfAnchors(POZYX_ANCHOR_SEL_AUTO, len(self._anchors))
        return status

    def check_pozyx_configuration(self):
        list_size = SingleRegister()
        self._pozyx.getDeviceListSize(list_size, self._remote_id)
        if list_size[0] != len(self._anchors):
            self.print_error("configuration")

    def do_positioning(self):
        """Performs positioning and displays the results."""
        if not self._is_initialized:
            print("error: pozyx not initialized")
            quit()
        position = Coordinates()
        status = self._pozyx.doPositioning(
            position, self._dimension, self._height, self._algorithm, remote_id=self._remote_id)
        if status == POZYX_SUCCESS:
            self.print_position(position)
        else:
            self.print_error("positioning")

    def print_position(self, position):
        """Prints the Pozyx's position"""
        print("x(mm): {pos.x} y(mm): {pos.y} z(mm): {pos.z}".format(pos=position))

    def print_error(self, operation):
        """Prints the Pozyx's error and possibly sends it as a OSC packet"""
        error_code = SingleRegister()
        self._pozyx.getErrorCode(error_code)
        print("LOCAL ERROR %s, %s" % (operation, self._pozyx.getErrorMessage(error_code)))

    def print_device_info(self):
        self._pozyx.printDeviceInfo(self._remote_id)

    def print_anchor_configuration(self):
        """Prints the anchor configuration result in a human-readable way."""
        list_size = SingleRegister()

        print("---------------------------------------------")
        print("Pozyx configuration:")
        self._pozyx.getDeviceListSize(list_size, self._remote_id)
        print("Device list size: {0}".format(list_size[0]))
        if list_size[0] != len(self._anchors):
            self.print_error("configuration")
            return
        device_list = DeviceList(list_size=list_size[0])
        self._pozyx.getDeviceIds(device_list, self._remote_id)
        print("Anchors found: {0}".format(list_size[0]))
        print("Anchor IDs: ", device_list)

        for i in range(list_size[0]):
            anchor_coordinates = Coordinates()
            self._pozyx.getDeviceCoordinates(device_list[i], anchor_coordinates, self._remote_id)
            print("ANCHOR, 0x%0.4x, %s" % (device_list[i], str(anchor_coordinates)))
        print("---------------------------------------------")

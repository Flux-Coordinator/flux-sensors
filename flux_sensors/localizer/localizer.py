#!/usr/bin/env python

from typing import List
from pypozyx import (Coordinates, DeviceCoordinates, SingleRegister, DeviceList, PozyxConstants,
                     get_first_pozyx_serial_port, PozyxSerial)
from flux_sensors.models import models

NUMBER_OF_CALIBRATION_CYCLES = 10

class LocalizerError(Exception):
    """Base class for exceptions in this module."""


class NoDeviceFoundError(LocalizerError):
    """Exception raised when no device is connected when attempting an access."""


class DeviceNotInitializedError(LocalizerError):
    """Exception raised when device is not initialized when starting the measurement."""


class DeviceConfigurationError(LocalizerError):
    """Exception raised when the configuration on the device is not consistent."""


class PozyxDeviceError(LocalizerError):
    """Custom Pozyx device Exception raised when receiving an error code from Pozyx."""


class Localizer(object):
    """Interface for 3D positioning with the Pozyx device"""

    def __init__(self, pozyx: PozyxSerial, anchors: List[DeviceCoordinates] = None,
                 dimension: PozyxConstants = PozyxConstants.POZYX_3D, height: int = 1000,
                 algorithm: PozyxConstants = PozyxConstants.POZYX_POS_ALG_TRACKING,
                 position_filter: PozyxConstants = PozyxConstants.FILTER_TYPE_MOVINGMEDIAN, filter_strength: int = 3,
                 remote_id: int = None) -> None:
        self._pozyx = pozyx
        self._anchors = []
        if anchors is not None:
            self._anchors = anchors
        self._dimension = dimension
        self._height = height
        self._algorithm = algorithm
        self._position_filter = position_filter
        self._filter_strength = filter_strength
        self._remote_id = remote_id
        self._is_initialized = False

    @staticmethod
    def get_device() -> PozyxSerial:
        serial_port = get_first_pozyx_serial_port()
        if serial_port is None:
            raise NoDeviceFoundError("No Pozyx device found. Check the cable connection or the driver.")
        return PozyxSerial(serial_port)

    def get_pozyx_error_message(self) -> str:
        """Returns the Pozyx's current error message"""
        error_code = SingleRegister()
        self._pozyx.getErrorCode(error_code, self._remote_id)
        return self._pozyx.getErrorMessage(error_code)

    def check_for_device_error(self, status: PozyxConstants) -> None:
        if status != PozyxConstants.POZYX_SUCCESS:
            raise PozyxDeviceError(self.get_pozyx_error_message())

    def check_for_initialization(self) -> None:
        if not self._is_initialized:
            raise DeviceNotInitializedError("Pozyx must be initialized to perform positioning")

    def is_initialized(self) -> bool:
        return self._is_initialized

    def add_anchor_to_cache(self, anchor_id: int, coordinates: Coordinates) -> None:
        self._is_initialized = False
        self._anchors.append(DeviceCoordinates(anchor_id, 1, coordinates))

    def clear_anchors_in_cache(self) -> None:
        self._is_initialized = False
        del self._anchors[:]

    def get_number_of_anchors_in_cache(self) -> int:
        return len(self._anchors)

    def initialize(self) -> None:
        """Sets up the Pozyx for positioning by calibrating its anchor list."""
        self.write_anchors_from_cache_to_device()
        self._pozyx.setPositionFilter(self._position_filter, self._filter_strength, self._remote_id)
        self.print_device_configuration()
        self.check_device_configuration()
        self._is_initialized = True
        self.calibratePositioning()

    def calibratePositioning(self) -> None:
        for i in range(0, NUMBER_OF_CALIBRATION_CYCLES):
            self.do_positioning()

    def clear(self) -> None:
        self._is_initialized = False
        self.clear_anchors_in_cache()

    def write_anchors_from_cache_to_device(self) -> None:
        """Adds the cached anchors to the Pozyx's device list one for one."""
        status = self._pozyx.clearDevices(self._remote_id)
        self.check_for_device_error(status)
        for anchor in self._anchors:
            status = self._pozyx.addDevice(anchor, self._remote_id)
            self.check_for_device_error(status)
        if len(self._anchors) > 4:
            status = self._pozyx.setSelectionOfAnchors(PozyxConstants.POZYX_ANCHOR_SEL_AUTO, len(self._anchors),
                                                       self._remote_id)
            self.check_for_device_error(status)

    def check_device_configuration(self) -> None:
        list_size = SingleRegister()
        status = self._pozyx.getDeviceListSize(list_size, self._remote_id)
        self.check_for_device_error(status)
        if list_size[0] != len(self._anchors):
            raise DeviceConfigurationError("The anchors configured in cache do not match with the list on the device.")
        if list_size[0] < 4:
            raise DeviceConfigurationError(
                "There must be at least 4 anchors configured to use Pozyx for 3D positioning")

    def do_positioning(self) -> models.Position:
        """Performs positioning and returns the results."""
        self.check_for_initialization()
        position = Coordinates()
        status = self._pozyx.doPositioning(
            position, self._dimension, self._height, self._algorithm, remote_id=self._remote_id)
        self.check_for_device_error(status)
        return models.Position(position.x, position.y, position.z)

    def print_device_info(self) -> None:
        self._pozyx.printDeviceInfo(self._remote_id)

    def print_device_configuration(self) -> None:
        """Prints the anchor configuration from the Pozyx device in a human-readable way."""
        list_size = SingleRegister()
        status = self._pozyx.getDeviceListSize(list_size, self._remote_id)
        self.check_for_device_error(status)

        device_list = DeviceList(list_size=list_size[0])
        status = self._pozyx.getDeviceIds(device_list, self._remote_id)
        self.check_for_device_error(status)

        print("---------------------------------------------")
        print("POZYX CONFIGURATION:")
        self._pozyx.printDeviceInfo(remote_id=self._remote_id)
        print("- Configured Devices:")
        self._pozyx.printDeviceList(remote_id=self._remote_id)
        print("---------------------------------------------")

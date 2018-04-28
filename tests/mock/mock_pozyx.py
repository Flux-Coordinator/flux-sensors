from typing import List
from pypozyx import (PozyxSerial, PozyxConstants, PozyxConnectionError, SingleRegister, Data, Coordinates, DeviceCoordinates, DeviceList)
from flux_sensors.models import models


class MockPozyx(PozyxSerial):

    def __init__(self, position: models.Position, error_code: int = 0x00, error_message: str = "none",
                 state: PozyxConstants = PozyxConstants.POZYX_SUCCESS) -> None:
        try:
            super().__init__("")
        except PozyxConnectionError:
            pass
        self._position = position
        self._error_code = error_code
        self._error_message = error_message
        self._state = state
        self._devices = []  # type: List[DeviceCoordinates]
        self._selection_is_set = False

    def getErrorCode(self, error_code: Data, remote_id: int = None) -> PozyxConstants:
        error_code.load(self._error_code)
        error_code = self._error_code
        return self._state

    def getErrorMessage(self, error_code: SingleRegister) -> str:
        return self._error_message

    def clearDevices(self, remote_id: int = None) -> PozyxConstants:
        del self._devices[:]
        return self._state

    def addDevice(self, device_coordinates: DeviceCoordinates, remote_id: int = None) -> PozyxConstants:
        self._devices.append(device_coordinates)
        return self._state

    def setSelectionOfAnchors(self, mode: int, number_of_anchors: int, remote_id: int = None) -> PozyxConstants:
        self._selection_is_set = True
        return self._state

    def getDeviceListSize(self, list_size: Data, remote_id: int = None) -> PozyxConstants:
        list_size.load([len(self._devices)])
        return self._state

    def doPositioning(self, position: Coordinates, dimension: int = PozyxConstants.POZYX_3D, height: int = 0,
                      algorithm: int = PozyxConstants.POZYX_POS_ALG_UWB_ONLY,
                      remote_id: int = None) -> PozyxConstants:
        pos = [self._position.get_x(), self._position.get_y(), self._position.get_z()]
        position.load(pos)
        return self._state

    def printDeviceInfo(self, remote_id: int = None) -> None:
        pass

    def getDeviceIds(self, device_list: DeviceList, remote_id: int = None) -> PozyxConstants:
        device_ids = []
        for device in self._devices:
            device_ids.append(device.network_id)
        device_list.load(device_ids)
        return self._state

    def getDeviceCoordinates(self, device_id: int, coordinates: Coordinates, remote_id: int = None) -> PozyxConstants:
        for device in self._devices:
            if device.network_id == device_id:
                coordinates.load(device.pos)
                return self._state

        return PozyxConstants.POZYX_FAILURE

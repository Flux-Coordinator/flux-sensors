#!/usr/bin/env python

from enum import IntEnum
from smbus2 import SMBus


class BitValues(IntEnum):
    BIT_0 = 0b00000001
    BIT_1 = 0b00000010
    BIT_2 = 0b00000100
    BIT_3 = 0b00001000
    BIT_4 = 0b00010000
    BIT_5 = 0b00100000
    BIT_6 = 0b01000000
    BIT_7 = 0b10000000


class ConfigRegister(IntEnum):
    ENABLE_REGISTER = 0x80  # Enables states and interrupts
    ATIME_REGISTER = 0x81  # ADC integration time (8bit value in 2.78ms intervals)
    WTIME_REGISTER = 0x83  # Time to wait between ALS cycles (8bit value in 2.78ms intervals)
    CFG0_REGISTER = 0x8D  # Configuration register one
    CFG1_REGISTER = 0x90  # Configuration register one
    ID_REGISTER = 0x92  # ID Register with Part Number Identification


class DataRegister(IntEnum):
    CH0DATAL_REGISTER = 0X94  # Low Byte of CH0 ADC data. Contains Z data.
    CH1DATAL_REGISTER = 0X96  # Low Byte of CH1 ADC data. Contains Y data.
    CH2DATAL_REGISTER = 0X98  # Low Byte of CH2 ADC data. Contains IR1 data.
    CH3DATAL_REGISTER = 0X9A  # Low Byte of CH3 ADC data. Contains X or IR2 data (depends on ALS_MULTIPLEXER).


# ENABLE_REGISTER
WAIT_ENABLE = BitValues.BIT_3  # This bit activates the wait feature. (1=enabled / 0=disabled)
ALS_ENABLE = BitValues.BIT_1  # This bit activates the ALS function (start measurement). (1=enabled / 0=disabled)
POWER_ON = BitValues.BIT_0  # This bit activates the internal oscillator (power ON). (1=enabled / 0=disabled)

# CFG0_REGISTER
RESET_CFG0 = BitValues.BIT_7  # Reserved. Must be set to 0b10000000.

# CFG1_REGISTER
ALS_MULTIPLEXER = BitValues.BIT_3  # Sets the CH3 input. (0=X-Channel (default) / 1=IR2)


class AlsGainControl(IntEnum):
    AGAIN_1x = 0b00
    AGAIN_4x = 0b01
    AGAIN_16x = 0b10
    AGAIN_64x = 0b11


class LightSensorError(Exception):
    """Base class for exceptions in this module."""


class SensorNotInitializedError(LightSensorError):
    """Exception raised when the light sensor is not initialized when starting the measurement."""


class LightSensor(object):
    """Interface to control the light sensor"""

    def __init__(self, device_address: int, device: SMBus) -> None:
        self._bus = device
        self._device_address = device_address
        self._is_initialized = False

    @staticmethod
    def get_device(i2c_port: int = 1):
        """0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)"""
        if i2c_port < 0 or i2c_port > 1:
            raise ValueError("Argument I2C-port must be between 0 and 1.")
        return SMBus(i2c_port)

    def check_for_initialization(self) -> None:
        if not self._is_initialized:
            raise SensorNotInitializedError("The light sensor must be initialized to perform measurements")

    def check_register_address(self, register_address: IntEnum) -> None:
        if register_address < 0x80 or register_address > 0xDD:
            raise ValueError("Register address out of range.")

    def is_initialized(self) -> bool:
        return self._is_initialized

    def read_register(self, register_address: IntEnum) -> int:
        self.check_register_address(register_address)
        return self._bus.read_byte_data(self._device_address, register_address)

    def write_register(self, register_address: IntEnum, bit_value: int) -> None:
        self.check_register_address(register_address)
        self._bus.write_byte_data(self._device_address, register_address, bit_value)

    def read_16bit_register(self, register_address: IntEnum) -> int:
        self.check_register_address(register_address)
        byte_values = self._bus.read_i2c_block_data(self._device_address, register_address, 2)
        return byte_values[1] * 256 + byte_values[0]

    def get_device_id(self) -> int:
        """Returns the 6 Bit Part Number Identification (e.g. 110111=TCS3430)"""
        return self.read_register(ConfigRegister.ID_REGISTER) >> 2

    def initialize(self, atime: int = 53, wtime: int = 0, wlong: int = 0) -> None:
        if atime < 0 or atime > 256:
            raise ValueError("Argument ATIME must be between 0 and 256.")
        elif wtime < 0 or wtime > 256:
            raise ValueError("Argument WTIME must be between 0 and 256.")
        elif wlong < 0 or wlong > 1:
            raise ValueError("Argument WLONG must be between 0 and 1.")

        self.write_register(ConfigRegister.ATIME_REGISTER, atime)
        self.write_register(ConfigRegister.WTIME_REGISTER, wtime)
        self.write_register(ConfigRegister.CFG0_REGISTER, RESET_CFG0 | (wlong * 4))
        self.write_register(ConfigRegister.CFG1_REGISTER, AlsGainControl.AGAIN_4x)

        self.startup()
        self.print_device_configuration()

        self._is_initialized = True

    def startup(self) -> None:
        self.write_register(ConfigRegister.ENABLE_REGISTER, ALS_ENABLE | POWER_ON)

    def print_device_configuration(self) -> None:
        print("---------------------------------------------")
        print("LIGHT SENSOR CONFIGURATION:")
        for register in ConfigRegister:
            configValue = self.read_register(register.value)
            print("{0: >16}\t0x{1:02x}\t{2:08b}\t{2}".format(register.name, register.value, configValue))
        print("---------------------------------------------")

    def do_measurement(self) -> float:
        self.check_for_initialization()
        y = self.read_y_data()
        return y  # The tristimulus value Y alone is defined as the luminance.

    def read_z_data(self) -> int:
        return self.read_16bit_register(DataRegister.CH0DATAL_REGISTER)

    def read_y_data(self) -> int:
        return self.read_16bit_register(DataRegister.CH1DATAL_REGISTER)

    def read_ir1_data(self) -> int:
        return self.read_16bit_register(DataRegister.CH2DATAL_REGISTER)

    def read_x_data(self) -> int:
        return self.read_16bit_register(DataRegister.CH3DATAL_REGISTER)

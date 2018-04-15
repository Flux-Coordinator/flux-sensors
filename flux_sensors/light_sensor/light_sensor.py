#!/usr/bin/env python

from enum import Enum
import smbus2, struct


# Registers and values
class BitValues(Enum):
    BIT_0 = 0b00000001
    BIT_1 = 0b00000010
    BIT_2 = 0b00000100
    BIT_3 = 0b00001000
    BIT_4 = 0b00010000
    BIT_5 = 0b00100000
    BIT_6 = 0b01000000
    BIT_7 = 0b10000000


ENABLE_REGISTER = 0x80 # Enables states and interrupts
WAIT_ENABLE = BitValues.BIT_3 # This bit activates the wait feature. (1=enabled / 0=disabled)
ALS_ENABLE = BitValues.BIT_1 # This bit activates the ALS function (start measurement). (1=enabled / 0=disabled)
POWER_ON = BitValues.BIT_0 # This bit activates the internal oscillator (power ON). (1=enabled / 0=disabled)

ATIME_REGISTER = 0x81 # ADC integration time (8bit value in 2.78ms intervals)

WTIME_REGISTER = 0x83 # Time to wait between ALS cycles (8bit value in 2.78ms intervals)

CFG0_REGISTER = 0x8D # Configuration register one
RESET_CFG0 = BitValues.BIT_7 # Reserved. Must be set to 0b10000000.

CFG1_REGISTER = 0x90 # Configuration register one
ALS_MULTIPLEXER = BitValues.BIT_3 # Sets the CH3 input. (0=X-Channel (default) / 1=IR2)


class AlsGainControl(Enum):
    AGAIN_1x = 0b00
    AGAIN_4x = 0b01
    AGAIN_16x = 0b10
    AGAIN_64x = 0b11


ID_REGISTER = 0x92

CH0DATAL_REGISTER = 0X94 # Low Byte of CH0 ADC data. Contains Z data.
CH1DATAL_REGISTER = 0X96 # Low Byte of CH1 ADC data. Contains Y data.
CH2DATAL_REGISTER = 0X98 # Low Byte of CH2 ADC data. Contains IR1 data.
CH3DATAL_REGISTER = 0X9A # Low Byte of CH3 ADC data. Contains X or IR2 data (depends on ALS_MULTIPLEXER).


class LightSensor(object):
    """Interface to control the light sensor"""

    def __init__(self, deviceAddress):
        self._bus = smbus2.SMBus(1) # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self._deviceAddress = deviceAddress
        self._isInitialized = False

    def read_register(self, registerAddress):
        return self._bus.read_byte_data(self._deviceAddress, registerAddress)

    def write_register(self, registerAddress, bitValue):
        self._bus.write_byte_data(self._deviceAddress, registerAddress, bitValue)

    def read_16bit_register(self, registerAddress):
        # todo check if initialized
        byteValues = self._bus.read_i2c_block_data(self._deviceAddress, registerAddress, 2)
        print("Low Value: {0:b}".format(byteValues[0]))
        print("High Value: {0:b}".format(byteValues[1]))
        print('\n')
        return byteValues[1] * 256 + byteValues[0]

    def get_device_id(self):
        """Returns the 6 Bit Part Number Identification (e.g. 110111=TCS3430)"""
        return self.read_register(ID_REGISTER) >> 2

    def initialize_sensor(self, atime=53, wtime=0, wlong=0):
        # todo check range of values
        self.write_register(ATIME_REGISTER, atime)
        self.write_register(WTIME_REGISTER, wtime)
        self.write_register(CFG0_REGISTER, RESET_CFG0 | (wlong * 4))
        self.write_register(CFG1_REGISTER, AlsGainControl.AGAIN_4x)
        self._isInitialized = True

    def startup(self):
        self.write_register(ENABLE_REGISTER, ALS_ENABLE | POWER_ON)

    def read_z_data(self):
        self.read_16bit_register(CH0DATAL_REGISTER)

    def read_y_data(self):
        self.read_16bit_register(CH1DATAL_REGISTER)

    def read_ir1_dData(self):
        self.read_16bit_register(CH2DATAL_REGISTER)

    def read_x_data(self):
        self.read_16bit_register(CH3DATAL_REGISTER)
from typing import Dict, List
from smbus2 import SMBus


class MockI2CBus(SMBus):

    def __init__(self, register: Dict[int, Dict[int, int]]) -> None:
        super().__init__()
        self._register = register

    def read_byte_data(self, device_address: int, register_address: int) -> int:
        return self._register.get(device_address).get(register_address)

    def write_byte_data(self, device_address: int, register_address: int, bit_value: int) -> None:
        self._register[device_address][register_address] = bit_value

    def read_i2c_block_data(self, device_address: int, register_address: int, length: int) -> List[int]:
        byte_values = []
        for i in range(0, length):
            byte_values.append(self._register[device_address][register_address + i])
        return byte_values

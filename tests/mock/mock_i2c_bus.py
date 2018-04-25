class MockI2CBus(object):

    def __init__(self, register):
        self._register = register

    def read_byte_data(self, device_address, register_address):
        return self._register.get(device_address).get(register_address)

    def write_byte_data(self, device_address, register_address, bit_value):
        self._register[device_address][register_address] = bit_value

    def read_i2c_block_data(self, device_address, register_address, length):
        byte_values = []
        for i in range(0, length):
            byte_values.append(self._register[device_address][register_address + i])
        return byte_values

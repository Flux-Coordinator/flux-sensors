import pytest
import json
from .context import flux_sensors
from flux_sensors.light_sensor.light_sensor import LightSensor
from .mock import mock_i2c_bus

mock_ams_register = {
    0x39: {
        0x80: 0,
        0x81: 0,
        0x83: 0,
        0x8D: 0,
        0x90: 0,
        0x92: 0,
        0X94: 255,
        0X95: 73,
        0X96: 123,
        0X97: 0,
        0X98: 128,
        0X99: 64,
        0X9A: 147,
        0X9B: 0
    }
}


class TestLightSensor(object):

    @pytest.fixture
    def ams_light_sensor(self) -> LightSensor:
        return LightSensor(0x39, mock_i2c_bus.MockI2CBus(mock_ams_register))

    def test_initialization(self, ams_light_sensor: LightSensor) -> None:
        ams_light_sensor.initialize()

        target_ams_register = {
            0x39: {
                0x80: 3,
                0x81: 53,
                0x83: 0,
                0x8D: 128,
                0x90: 1,
                0x92: 0,
                0X94: 255,
                0X95: 73,
                0X96: 123,
                0X97: 0,
                0X98: 128,
                0X99: 64,
                0X9A: 147,
                0X9B: 0
            }
        }

        mock_ams_register_json = json.dumps(mock_ams_register, sort_keys=True)
        target_ams_register_json = json.dumps(target_ams_register, sort_keys=True)

        assert mock_ams_register_json == target_ams_register_json

    def test_measurement(self, ams_light_sensor: LightSensor) -> None:
        ams_light_sensor.initialize()
        illuminance = ams_light_sensor.do_measurement()
        assert illuminance == 19213

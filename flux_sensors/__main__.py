from flux_sensors.localizer.localizer import Localizer
from flux_sensors.light_sensor.light_sensor import LightSensor
from flux_sensors.flux_sensor import FluxSensor
from flux_sensors.config_loader import ConfigLoader
from flux_sensors.flux_server import FluxServer

AMS_LIGHT_SENSOR_I2C_ADDRESS = 0x39


def main() -> None:
    """entry point"""
    pozyx = Localizer.get_device()
    pozyx_localizer = Localizer(pozyx)

    ams_device = LightSensor.get_device(1)
    ams_light_sensor = LightSensor(AMS_LIGHT_SENSOR_I2C_ADDRESS, ams_device)

    config_loader = ConfigLoader()

    flux_server = FluxServer()

    flux_sensor = FluxSensor(pozyx_localizer, ams_light_sensor, config_loader, flux_server)
    flux_sensor.start_when_ready()


if __name__ == "__main__":
    main()

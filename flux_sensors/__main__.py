import sys
import logging
from flux_sensors.localizer.localizer import Localizer
from flux_sensors.light_sensor.light_sensor import LightSensor
from flux_sensors.flux_sensor import FluxSensor
from flux_sensors.config_loader import ConfigLoader
from flux_sensors.flux_server import FluxServer

AMS_LIGHT_SENSOR_I2C_ADDRESS = 0x39

logger = logging.getLogger('flux_sensors')


def setup_logging(verbose=False, quiet=False):
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(levelname)-7s] - %(message)s')
    if quiet:
        logger.setLevel(logging.WARNING)
    elif verbose:
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)-7s] - %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def main() -> None:
    """entry point"""
    setup_logging(verbose=False)

    pozyx = Localizer.get_device()
    pozyx_localizer = Localizer(pozyx)

    ams_device = LightSensor.get_device(1)
    ams_light_sensor = LightSensor(AMS_LIGHT_SENSOR_I2C_ADDRESS, ams_device)

    config_loader = ConfigLoader()

    flux_server = FluxServer(config_loader.get_credentials())

    flux_sensor = FluxSensor(pozyx_localizer, ams_light_sensor, config_loader, flux_server)
    flux_sensor.start_when_ready()


if __name__ == "__main__":
    main()

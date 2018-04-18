from flux_sensors.localizer import localizer
from flux_sensors.light_sensor import light_sensor
import time
import datetime


AMS_LIGHT_SENSOR_I2C_ADDRESS = 0x39


def main():
    """entry point"""
    localizer_instance = initialize_localizer()
    light_sensor_instance = initialize_light_sensor()
    start_measurement(localizer_instance, light_sensor_instance)


def initialize_localizer():
    pozyx = localizer.Localizer.get_device()
    pozyx_localizer = localizer.Localizer(pozyx)

    pozyx_localizer.add_anchor_to_cache(0x6e4e, localizer.Coordinates(-100, 100, 1150))
    pozyx_localizer.add_anchor_to_cache(0x6964, localizer.Coordinates(8450, 1200, 2150))
    pozyx_localizer.add_anchor_to_cache(0x6e5f, localizer.Coordinates(1250, 12000, 1150))
    pozyx_localizer.add_anchor_to_cache(0x6e62, localizer.Coordinates(7350, 11660, 1590))

    pozyx_localizer.initialize()
    return pozyx_localizer


def initialize_light_sensor():
    ams_device = light_sensor.LightSensor.get_device(1)
    ams_light_sensor = light_sensor.LightSensor(AMS_LIGHT_SENSOR_I2C_ADDRESS, ams_device)

    ams_light_sensor.initialize()
    return ams_light_sensor


def start_measurement(localizer_instance, light_sensor_instance):
    while True:
        time_stamp = time.time()
        formatted_time_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
        print("{0}/{1}/{2}".format(formatted_time_stamp, localizer_instance.do_positioning(),
                                   light_sensor_instance.do_measurement()))


if __name__ == "__main__":
    main()

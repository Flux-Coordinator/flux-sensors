from flux_sensors.localizer import localizer
from flux_sensors.light_sensor import light_sensor
import time
import datetime
import polling
import requests

AMS_LIGHT_SENSOR_I2C_ADDRESS = 0x39


def main():
    """entry point"""
    start_when_ready()


def start_when_ready():
    polling.poll(
        lambda: requests.get('https://www.hsr.ch'),
        check_success=initialize_sensors,
        step=3,
        ignore_exceptions=requests.exceptions.ConnectionError,
        poll_forever=True)


def initialize_sensors(response):
    print("Success! Response: {0}".format(response.status_code))
    pozyx = localizer.Localizer.get_device()
    pozyx_localizer = localizer.Localizer(pozyx)
    initialize_localizer(pozyx_localizer)

    ams_device = light_sensor.LightSensor.get_device(1)
    ams_light_sensor = light_sensor.LightSensor(AMS_LIGHT_SENSOR_I2C_ADDRESS, ams_device)
    initialize_light_sensor(ams_light_sensor)

    start_measurement(pozyx_localizer, ams_light_sensor)


def initialize_localizer(localizer_instance):
    localizer_instance.add_anchor_to_cache(0x6e4e, localizer.Coordinates(-100, 100, 1150))
    localizer_instance.add_anchor_to_cache(0x6964, localizer.Coordinates(8450, 1200, 2150))
    localizer_instance.add_anchor_to_cache(0x6e5f, localizer.Coordinates(1250, 12000, 1150))
    localizer_instance.add_anchor_to_cache(0x6e62, localizer.Coordinates(7350, 11660, 1590))

    localizer_instance.initialize()


def initialize_light_sensor(light_sensor_instance):
    light_sensor_instance.initialize()


def start_measurement(localizer_instance, light_sensor_instance):
    while True:
        time_stamp = time.time()
        formatted_time_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
        print("{0}/{1}/{2}".format(formatted_time_stamp, localizer_instance.do_positioning(),
                                   light_sensor_instance.do_measurement()))


if __name__ == "__main__":
    main()

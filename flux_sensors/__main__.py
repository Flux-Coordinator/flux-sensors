from flux_sensors.localizer import localizer
from flux_sensors.light_sensor import light_sensor
from flux_sensors.models import models
import time
import datetime
import polling
import requests
import json

AMS_LIGHT_SENSOR_I2C_ADDRESS = 0x39
SERVER_URL = "http://localhost:9000"
CHECK_ACTIVE_MEASUREMENT_ROUTE = "/measurements/active"
ADD_READINGS_ROUTE = "/measurements/active/readings"


def main():
    """entry point"""
    start_when_ready()


def start_when_ready():
    polling.poll(
        lambda: requests.get(SERVER_URL + CHECK_ACTIVE_MEASUREMENT_ROUTE).status_code == 200,
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
        position = localizer_instance.do_positioning()
        illuminance = light_sensor_instance.do_measurement()

        payload = models.Reading(illuminance, position)
        json_data = json.dumps(payload.__dict__)

        requests.post(SERVER_URL + ADD_READINGS_ROUTE, json=payload)
        print(json_data)


if __name__ == "__main__":
    main()

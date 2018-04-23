from flux_sensors.localizer import localizer
from flux_sensors.light_sensor import light_sensor
from flux_sensors.models import models
import polling
import requests
import json

AMS_LIGHT_SENSOR_I2C_ADDRESS = 0x39
SERVER_URL = "http://localhost:9000"
CHECK_ACTIVE_MEASUREMENT_ROUTE = "/measurements/active"
ADD_READINGS_ROUTE = "/measurements/active/readings"


def main():
    """entry point"""
    pozyx = localizer.Localizer.get_device()
    pozyx_localizer = localizer.Localizer(pozyx)

    ams_device = light_sensor.LightSensor.get_device(1)
    ams_light_sensor = light_sensor.LightSensor(AMS_LIGHT_SENSOR_I2C_ADDRESS, ams_device)

    flux_sensor = FluxSensor(pozyx_localizer, ams_light_sensor)
    flux_sensor.start_when_ready()


class FluxSensor(object):
    """Controlling class for the flux-sensors components"""

    def __init__(self, localizer_instance, light_sensor_instance):
        self._localizer = localizer_instance
        self._light_sensor = light_sensor_instance
        self._check_ready_counter = 0

    def start_when_ready(self):
        polling.poll(
            target=lambda: requests.get(SERVER_URL + CHECK_ACTIVE_MEASUREMENT_ROUTE),
            check_success=self.check_if_server_ready,
            step=3,
            ignore_exceptions=(requests.exceptions.ConnectionError,),
            poll_forever=True)

        self.initialize_sensors()
        self.start_measurement()

    def check_if_server_ready(self, response):
        self._check_ready_counter += 1
        print("Polling flux-server. Try {}".format(self._check_ready_counter))
        return response.status_code == 200

    def initialize_sensors(self):
        print("Success! A flux-server is available and a measurement is active.")

        self.initialize_localizer()
        self.initialize_light_sensor()

    def initialize_localizer(self):
        self._localizer.add_anchor_to_cache(0x6e4e, localizer.Coordinates(-100, 100, 1150))
        self._localizer.add_anchor_to_cache(0x6964, localizer.Coordinates(8450, 1200, 2150))
        self._localizer.add_anchor_to_cache(0x6e5f, localizer.Coordinates(1250, 12000, 1150))
        self._localizer.add_anchor_to_cache(0x6e62, localizer.Coordinates(7350, 11660, 1590))

        self._localizer.initialize()

    def initialize_light_sensor(self):
        self._light_sensor.initialize()

    def start_measurement(self):
        while True:
            position = self._localizer.do_positioning()
            illuminance = self._light_sensor.do_measurement()

            reading = models.Reading(illuminance, position)
            readings = []
            readings.append(reading)

            json_data = json.dumps(readings, default=lambda o: o.__dict__)

            headers = {'content-type': 'application/json'}
            requests.post(SERVER_URL + ADD_READINGS_ROUTE, data=json_data, headers=headers)
            print(json_data)


if __name__ == "__main__":
    main()

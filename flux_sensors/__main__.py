from flux_sensors.localizer.localizer import Localizer, Coordinates
from flux_sensors.light_sensor.light_sensor import LightSensor
from flux_sensors.models import models
from http.client import responses
import polling
import requests
import json

AMS_LIGHT_SENSOR_I2C_ADDRESS = 0x39
SERVER_URL = "http://localhost:9000"


def main() -> None:
    """entry point"""
    pozyx = Localizer.get_device()
    pozyx_localizer = Localizer(pozyx)

    ams_device = LightSensor.get_device(1)
    ams_light_sensor = LightSensor(AMS_LIGHT_SENSOR_I2C_ADDRESS, ams_device)

    flux_sensor = FluxSensor(pozyx_localizer, ams_light_sensor, SERVER_URL)
    print("Flux-sensors available.")
    while True:
        print("Start measurement when server ready...")
        flux_sensor.wait_for_server_readiness()
        print("Success! A flux-server is available and a measurement is active.")
        flux_sensor.initialize_sensors()
        flux_sensor.start_measurement()
        flux_sensor.clear_sensors()


class FluxSensor(object):
    """Controlling class for the flux-sensors components"""

    CHECK_ACTIVE_MEASUREMENT_ROUTE = "/measurements/active"
    ADD_READINGS_ROUTE = "/measurements/active/readings"

    def __init__(self, localizer_instance: Localizer, light_sensor_instance: LightSensor, server_url: str) -> None:
        self._localizer = localizer_instance
        self._light_sensor = light_sensor_instance
        self._server_url = server_url
        self._check_ready_counter = 0

    def wait_for_server_readiness(self) -> None:
        self._check_ready_counter = 0
        polling.poll(
            target=lambda: requests.get(self._server_url + self.CHECK_ACTIVE_MEASUREMENT_ROUTE),
            check_success=self.check_polling_success,
            step=3,
            step_function=self.log_polling_step,
            ignore_exceptions=(requests.exceptions.ConnectionError,),
            poll_forever=True)

    def check_polling_success(self, response: requests.Response) -> bool:
        self.log_server_response(response)
        return response.status_code == 200

    def log_polling_step(self, step: int) -> int:
        self._check_ready_counter += 1
        print("Polling Flux-server at {}: {} attempt(s)".format(self._server_url + self.CHECK_ACTIVE_MEASUREMENT_ROUTE,
                                                                self._check_ready_counter))
        return step

    def log_server_response(self, response: requests.Response) -> None:
        description = ""
        if response.status_code == 204:
            description = " -> no active measurement available"
        elif response.status_code == 400:
            description = " -> check firewall settings or AllowedHostsFilter from flux-server"
        print("Response: {} ({}){}".format(response.status_code, responses[response.status_code],
                                           description))

    def initialize_sensors(self) -> None:
        self.initialize_localizer()
        self.initialize_light_sensor()

    def initialize_localizer(self) -> None:
        self._localizer.add_anchor_to_cache(0x6e4e, Coordinates(-100, 100, 1150))
        self._localizer.add_anchor_to_cache(0x6964, Coordinates(8450, 1200, 2150))
        self._localizer.add_anchor_to_cache(0x6e5f, Coordinates(1250, 12000, 1150))
        self._localizer.add_anchor_to_cache(0x6e62, Coordinates(7350, 11660, 1590))

        self._localizer.initialize()

    def initialize_light_sensor(self) -> None:
        self._light_sensor.initialize()

    def clear_sensors(self) -> None:
        self._localizer.clear()

    def start_measurement(self) -> None:
        while True:
            position = self._localizer.do_positioning()
            illuminance = self._light_sensor.do_measurement()

            reading = models.Reading(illuminance, position)
            readings = [reading]
            json_data = json.dumps(readings, default=lambda o: o.__dict__)

            response = self.send_data_to_server(json_data)
            self.log_server_response(response)

            if response.status_code == 204:
                print("The measurement has been stopped by the server.")
                return
            elif response.status_code != 200:
                print("The measurement has been stopped.")
                return

    def send_data_to_server(self, json_data: str) -> requests.Response:
        print("Sending: {}".format(json_data))
        headers = {'content-type': 'application/json'}
        return requests.post(self._server_url + self.ADD_READINGS_ROUTE, data=json_data, headers=headers)


if __name__ == "__main__":
    main()

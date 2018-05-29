from flux_sensors.localizer.localizer import Localizer, Coordinates
from flux_sensors.light_sensor.light_sensor import LightSensor
from flux_sensors.config_loader import ConfigLoader
from flux_sensors.flux_server import FluxServer
from flux_sensors.models import models
import time
import requests
import json


class FluxSensorError(Exception):
    """Base class for exceptions in this module."""


class InitializationError(FluxSensorError):
    """Exception raised when the initialization of the sensors failed."""


class FluxSensor:
    """Controlling class for the flux-sensors components"""

    def __init__(self, localizer_instance: Localizer, light_sensor_instance: LightSensor, config_loader: ConfigLoader,
                 flux_server: FluxServer) -> None:
        self._localizer = localizer_instance
        self._light_sensor = light_sensor_instance
        self._config_loader = config_loader
        self._flux_server = flux_server

    def start_when_ready(self) -> None:
        print("Flux-sensors in standby. Start polling Flux-server")
        while True:
            if not self._flux_server.poll_server_urls(self._config_loader.get_server_urls(),
                                                      self._config_loader.get_timeout()):
                print("All server URLs failed to respond. Retry started...")
                continue
            print("Server responding. Start measurement when ready...")

            if not self._flux_server.poll_active_measurement():
                continue
            print("Success! A flux-server is available and a measurement is active.")

            try:
                response = self._flux_server.get_active_measurement()
                self._flux_server.log_server_response(response)
            except requests.exceptions.RequestException as err:
                print("Request error while loading active measurement from Flux-server")
                print(err)
                FluxSensor.handle_retry(3)
                continue

            try:
                self.initialize_sensors(response.text)
            except InitializationError as err:
                print("Error while initializing the sensors")
                print(err)
                FluxSensor.handle_retry(3)
                continue

            print("Flux-sensors initialized. Start measurement...")
            self.start_measurement()
            self.clear_sensors()

    @staticmethod
    def handle_retry(seconds: int) -> None:
        print("Retry starts in {} seconds...".format(seconds))
        time.sleep(seconds)

    def initialize_sensors(self, measurement: str) -> None:
        self.initialize_localizer(measurement)
        self.initialize_light_sensor()

    def initialize_localizer(self, measurement: str) -> None:
        try:
            measurement_json = json.loads(measurement)
            print("test start:")
            for anchorPosition in measurement_json["anchorPositions"]:
                self._localizer.add_anchor_to_cache(int(anchorPosition["anchor"]["networkId"], 16),
                                                    Coordinates(int(anchorPosition["xposition"]),
                                                                int(anchorPosition["yposition"]),
                                                                int(anchorPosition["zposition"])))
        except(ValueError, KeyError, TypeError):
            raise InitializationError("Error while parsing the Pozyx Anchors.")

        self._localizer.initialize()

    def initialize_light_sensor(self) -> None:
        self._light_sensor.initialize()

    def clear_sensors(self) -> None:
        self._localizer.clear()

    def start_measurement(self) -> None:
        readings = []
        while True:
            position = self._localizer.do_positioning()
            illuminance = self._light_sensor.do_measurement()

            readings.append(models.Reading(illuminance, position))

            try:
                if self._flux_server.get_last_response() == 200:
                    if len(readings) >= self._flux_server.MIN_BATCH_SIZE:
                        self._flux_server.reset_last_response()
                        json_data = json.dumps(readings, default=lambda o: o.__dict__)
                        self._flux_server.send_data_to_server(json_data)
                        del readings[:]
                elif self._flux_server.get_last_response() == 404:
                    print("The measurement has been stopped by the server.")
                    return
                elif self._flux_server.get_last_response() != self._flux_server.RESPONSE_PENDING:
                    print("The measurement has been stopped.")
                    return
            except requests.exceptions.RequestException as err:
                print(err)
                return

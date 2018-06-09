from typing import List, Dict, Optional, Callable
import polling
from http.client import responses
import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import Future
import logging

CHECK_SERVER_READY_ROUTE = ""
CHECK_ACTIVE_MEASUREMENT_ROUTE = "/measurements/active"
ADD_READINGS_ROUTE = "/measurements/active/readings"
LOGIN_ROUTE = "/login"

logger = logging.getLogger(__name__)


class FluxServerError(Exception):
    """Base class for exceptions in this module."""


class AuthorizationError(FluxServerError):
    """Exception raised when the authorization failed."""


class FluxServer:
    RESPONSE_PENDING = 0
    MIN_BATCH_SIZE = 3
    CONTENT_TYPE_HEADER = "content-type"
    AUTHORIZATION_HEADER = "Authorization"
    SENSOR_DEVICE_HEADER = "X-Flux-Sensor"

    @staticmethod
    def log_server_response(response: requests.Response) -> None:
        description = ""
        if response.status_code == 204:
            description = " -> no active measurement available"
        elif response.status_code == 400:
            description = " -> check firewall settings or AllowedHostsFilter from flux-server"
        logger.info("Response: {} ({}){}".format(response.status_code, responses[response.status_code],
                                                 description))

    def __init__(self) -> None:
        self._check_ready_counter = 0
        self._server_url = ""
        self._poll_route = ""
        self._session = FuturesSession()
        self._last_response = 200
        self._auth_token = ""

    def _get_headers(self) -> Dict[str, str]:
        return {FluxServer.AUTHORIZATION_HEADER: self._auth_token, FluxServer.SENSOR_DEVICE_HEADER: ''}

    def poll_server_urls(self, server_urls: List[str], timeout: Optional[int] = 3) -> bool:
        for server_url in server_urls:
            if self._poll_server_route(server_url, CHECK_SERVER_READY_ROUTE, timeout):
                self._server_url = server_url
                return True
        return False

    def poll_active_measurement(self) -> bool:
        return self._poll_server_route(self._server_url, CHECK_ACTIVE_MEASUREMENT_ROUTE)

    def _poll_server_route(self, server_url: str, route: str, timeout: Optional[int] = None) -> bool:
        self._check_ready_counter = 0
        self._server_url = server_url
        self._poll_route = route

        logger.info("Polling Flux-server at {}".format(self._server_url + self._poll_route))

        ignore_exceptions = (requests.exceptions.RequestException,)
        poll_forever = False
        if timeout is None:
            ignore_exceptions = ()
            poll_forever = True

        try:
            polling.poll(
                target=lambda: requests.get(server_url + route, headers=self._get_headers()),
                check_success=self._check_polling_success,
                step=2,
                step_function=self._log_polling_step,
                ignore_exceptions=ignore_exceptions,
                timeout=timeout,
                poll_forever=poll_forever)
        except polling.TimeoutException:
            logger.error("Polling timeout ({}s) exceeded.".format(timeout))
            return False
        except requests.exceptions.RequestException as re:
            logger.error("Error: RequestException {}".format(str(re)))
            if re.response is not None:
                self.log_server_response(re.response)
            return False
        except AuthorizationError as error:
            logger.error(error)
            return False

        return True

    def _check_polling_success(self, response: requests.Response) -> bool:
        self.log_server_response(response)
        if response.status_code == 401:
            self.login_at_server()
        return response.status_code == 200

    def _log_polling_step(self, step: int) -> int:
        self._check_ready_counter += 1
        logger.info("Polling Flux-server at {}: retry {}".format(self._server_url + self._poll_route,
                                                                 self._check_ready_counter))
        return step

    def get_active_measurement(self) -> requests.Response:
        return self.login_if_unauthorized(
            lambda: requests.get(self._server_url + CHECK_ACTIVE_MEASUREMENT_ROUTE, headers=self._get_headers()))

    def initialize_last_response(self):
        self._last_response = 200

    def reset_last_response(self):
        self._last_response = self.RESPONSE_PENDING

    def get_last_response(self):
        return self._last_response

    def _post_callback(self, sess: FuturesSession, resp: requests.Response):
        self._last_response = resp.status_code
        self.log_server_response(resp)

    def send_data_to_server(self, json_data: str) -> Future:
        logger.info("Sending: {}".format(json_data))
        headers = self._get_headers()
        headers[FluxServer.CONTENT_TYPE_HEADER] = 'application/json'
        return self._session.post(self._server_url + ADD_READINGS_ROUTE, data=json_data, headers=headers,
                                  background_callback=self._post_callback)

    def login_at_server(self):
        if self._server_url != "":
            login_route = self._server_url + LOGIN_ROUTE
            response = requests.get(login_route)
            if response == 401:
                raise AuthorizationError(
                    "Login Flux-server at {} failed. Wrong password or username configured.".format(login_route))
            self._auth_token = response.text
            logger.info("Login Flux-server at {} successful".format(login_route))

    def login_if_unauthorized(self, server_request: Callable[[], requests.Response]) -> requests.Response:
        response = server_request()
        if response.status_code == 401:
            self.login_at_server()
            response = server_request()
        return response

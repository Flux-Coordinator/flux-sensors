from typing import List, Optional
import polling
from http.client import responses
import requests

CHECK_SERVER_READY_ROUTE = ""
CHECK_ACTIVE_MEASUREMENT_ROUTE = "/measurements/active"
ADD_READINGS_ROUTE = "/measurements/active/readings"


class ServerProbe:

    @staticmethod
    def log_server_response(response: requests.Response) -> None:
        description = ""
        if response.status_code == 204:
            description = " -> no active measurement available"
        elif response.status_code == 400:
            description = " -> check firewall settings or AllowedHostsFilter from flux-server"
        print("Response: {} ({}){}".format(response.status_code, responses[response.status_code],
                                           description))

    def __init__(self) -> None:
        self._check_ready_counter = 0
        self._server_url = ""
        self._poll_route = ""

    def poll_server_urls(self, server_urls: List[str], timeout: Optional[int] = 10) -> bool:
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

        print("Polling Flux-server at {}".format(self._server_url + self._poll_route))

        ignore_exceptions = (requests.exceptions.RequestException,)
        poll_forever = False
        if timeout is None:
            ignore_exceptions = ()
            poll_forever = True

        try:
            polling.poll(
                target=lambda: requests.get(server_url + route),
                check_success=self._check_polling_success,
                step=3,
                step_function=self._log_polling_step,
                ignore_exceptions=ignore_exceptions,
                timeout=timeout,
                poll_forever=poll_forever)
        except polling.TimeoutException:
            print("Polling timeout ({}s) exceeded.".format(timeout))
            return False
        except requests.exceptions.RequestException as re:
            self.log_server_response(re.response)
            return False
        return True

    def _check_polling_success(self, response: requests.Response) -> bool:
        self.log_server_response(response)
        return response.status_code == 200

    def _log_polling_step(self, step: int) -> int:
        self._check_ready_counter += 1
        print("Polling Flux-server at {}: retry {}".format(self._server_url + self._poll_route,
                                                           self._check_ready_counter))
        return step

    def send_data_to_server(self, json_data: str) -> requests.Response:
        print("Sending: {}".format(json_data))
        headers = {'content-type': 'application/json'}
        return requests.post(self._server_url + ADD_READINGS_ROUTE, data=json_data, headers=headers)

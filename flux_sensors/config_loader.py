from typing import List, Optional
import configparser
import logging

CONFIG_FILE_PATH = "/home/pi/.config/flux-config.ini"
SECTION_FLUX_SERVER_URLS = "Flux Server URLs"
SECTION_FLUX_SERVER_CONNECTION_SETTINGS = "Flux Server Connection Settings"
DEFAULT_FLUX_SERVER_URL = "http://localhost:9000"
DEFAULT_FLUX_SERVER_CONNECTION_TIMEOUT = 10

logger = logging.getLogger(__name__)


class ConfigLoader:

    def __init__(self) -> None:
        self._timeout = DEFAULT_FLUX_SERVER_CONNECTION_TIMEOUT
        self._server_urls = []
        self._load_config()

    def _load_config(self) -> None:
        logger.info("Load config file '{}'...".format(CONFIG_FILE_PATH))
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        self._load_connection_settings(config)
        self._load_server_urls(config)

    def _load_connection_settings(self, config: configparser.ConfigParser) -> None:
        flux_server_connection_settings = self._load_section(config, SECTION_FLUX_SERVER_CONNECTION_SETTINGS)
        self._timeout = self._load_int_value(flux_server_connection_settings, "timeout",
                                             DEFAULT_FLUX_SERVER_CONNECTION_TIMEOUT)

    def _load_server_urls(self, config: configparser.ConfigParser) -> None:
        flux_server_urls = self._load_section(config, SECTION_FLUX_SERVER_URLS)

        if flux_server_urls is None:
            self._server_urls.append(DEFAULT_FLUX_SERVER_URL)
            return

        logger.info("FLUX-server URLs loaded:")
        for key in flux_server_urls:
            logger.info(key + ": " + flux_server_urls[key])
            self._server_urls.append(flux_server_urls[key])

    def _load_section(self, config: configparser.ConfigParser, key: str) -> Optional[configparser.ConfigParser]:
        try:
            return config[key]
        except KeyError:
            logger.error("Error: config file has missing section '{}'. Using default values instead".format(key))
            return None

    def _load_int_value(self, section: Optional[configparser.ConfigParser], key: str, default_value: int) -> int:
        if section is None:
            return default_value
        try:
            return section.getint(key, default_value)
        except ValueError:
            logger.error(
                "Error: config file has wrong format for value '{}'. Using default value {} instead".format(key,
                                                                                                            default_value))

    def get_timeout(self) -> int:
        return self._timeout

    def get_server_urls(self) -> List[str]:
        return self._server_urls

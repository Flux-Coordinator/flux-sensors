import pytest
from .context import flux_sensors
from flux_sensors.localizer.localizer import Localizer
from .mock import mock_pozyx
from flux_sensors.models import models
from pypozyx import (Coordinates)

TEST_POSITION = models.Position(1000, 2000, 3000)


class TestLocalizer(object):

    @pytest.fixture
    def pozyx_localizer(self) -> Localizer:
        return Localizer(mock_pozyx.MockPozyx(TEST_POSITION))

    def test_initialization(self, pozyx_localizer: Localizer) -> None:
        self.add_fake_anchors(pozyx_localizer)
        pozyx_localizer.initialize()

    def test_measurement(self, pozyx_localizer: Localizer) -> None:
        self.add_fake_anchors(pozyx_localizer)
        pozyx_localizer.initialize()
        position = pozyx_localizer.do_positioning()
        assert position.get_x() == TEST_POSITION.get_x()
        assert position.get_y() == TEST_POSITION.get_y()
        assert position.get_z() == TEST_POSITION.get_z()

    def add_fake_anchors(self, pozyx_localizer_instance: Localizer) -> None:
        pozyx_localizer_instance.add_anchor_to_cache(0x6e4e, Coordinates(-100, 100, 1150))
        pozyx_localizer_instance.add_anchor_to_cache(0x6964, Coordinates(8450, 1200, 2150))
        pozyx_localizer_instance.add_anchor_to_cache(0x6e5f, Coordinates(1250, 12000, 1150))
        pozyx_localizer_instance.add_anchor_to_cache(0x6e62, Coordinates(7350, 11660, 1590))

from flux_sensors.localizer import localizer
from flux_sensors.light_sensor import light_sensor


def main():
    """entry point"""
    initialize_sensors()
    start_measurement()


pozyx_localizer = None


def initialize_sensors():
    global pozyx_localizer

    pozyx = localizer.Localizer.get_device()
    pozyx_localizer = localizer.Localizer(pozyx)

    pozyx_localizer.add_anchor_to_cache(0x6e4e, localizer.Coordinates(-100, 100, 1150))
    pozyx_localizer.add_anchor_to_cache(0x6964, localizer.Coordinates(8450, 1200, 2150))
    pozyx_localizer.add_anchor_to_cache(0x6e5f, localizer.Coordinates(1250, 12000, 1150))
    pozyx_localizer.add_anchor_to_cache(0x6e62, localizer.Coordinates(7350, 11660, 1590))

    pozyx_localizer.initialize()


def start_measurement():
    while True:
        print(pozyx_localizer.do_positioning())


if __name__ == "__main__":
    main()

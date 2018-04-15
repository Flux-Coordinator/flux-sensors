from flux_sensors.localizer import localizer


def main():
    """entry point"""
    run_pozyx()


def run_pozyx():
    serial_port = localizer.get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    pozyx = localizer.PozyxSerial(serial_port)
    pozyx_localizer = localizer.Localizer(pozyx)

    pozyx_localizer.add_anchor(0x6e4e, localizer.Coordinates(-100, 100, 1150))
    pozyx_localizer.add_anchor(0x6964, localizer.Coordinates(8450, 1200, 2150))
    pozyx_localizer.add_anchor(0x6e5f, localizer.Coordinates(1250, 12000, 1150))
    pozyx_localizer.add_anchor(0x6e62, localizer.Coordinates(7350, 11660, 1590))

    pozyx_localizer.initialize()
    while True:
        pozyx_localizer.do_positioning()


if __name__ == "__main__":
    main()

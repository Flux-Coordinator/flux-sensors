from flux_sensors.localizer import localizer


def main():
    """entry point"""
    runPozyx()


def runPozyx():
    serial_port = localizer.get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    remote_id = 0x6069  # remote device network ID
    remote = False  # whether to use a remote device
    if not remote:
        remote_id = None

    use_processing = True  # enable to send position data through OSC
    ip = "127.0.0.1"  # IP for the OSC UDP
    network_port = 8888  # network port for the OSC UDP
    osc_udp_client = None
    if use_processing:
        osc_udp_client = localizer.SimpleUDPClient(ip, network_port)
    # necessary data for calibration, change the IDs and coordinates yourself
    anchors = [localizer.DeviceCoordinates(0x6e4e, 1, localizer.Coordinates(-100, -100, 1150)),
               localizer.DeviceCoordinates(0x6964, 1, localizer.Coordinates(8450, -1200, 2150)),
               localizer.DeviceCoordinates(0x6e5f, 1, localizer.Coordinates(1250, -12000, 1150)),
               localizer.DeviceCoordinates(0x6e62, 1, localizer.Coordinates(7350, -11660, 1590))]

    algorithm = localizer.POZYX_POS_ALG_UWB_ONLY  # positioning algorithm to use
    dimension = localizer.POZYX_3D  # positioning dimension
    height = 1000  # height of device, required in 2.5D positioning

    pozyx = localizer.PozyxSerial(serial_port)
    r = localizer.Localizer(pozyx, osc_udp_client, anchors, algorithm, dimension, height, remote_id)
    r.setup()
    while True:
        r.loop()


if __name__ == "__main__":
    main()

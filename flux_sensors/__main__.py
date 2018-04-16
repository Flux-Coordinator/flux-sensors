from flux_sensors.localizer import localizer
from flux_sensors.light_sensor import light_sensor


def main():
    """entry point"""
    initialize_sensors()
    start_measurement()


AMS_LIGHT_SENSOR_I2C_ADDRESS = 0x39

pozyx_localizer = None
ams_light_sensor = None


def initialize_sensors():
    global pozyx_localizer
    global ams_light_sensor

    pozyx = localizer.Localizer.get_device()
    pozyx_localizer = localizer.Localizer(pozyx)

    pozyx_localizer.add_anchor_to_cache(0x6e4e, localizer.Coordinates(-100, 100, 1150))
    pozyx_localizer.add_anchor_to_cache(0x6964, localizer.Coordinates(8450, 1200, 2150))
    pozyx_localizer.add_anchor_to_cache(0x6e5f, localizer.Coordinates(1250, 12000, 1150))
    pozyx_localizer.add_anchor_to_cache(0x6e62, localizer.Coordinates(7350, 11660, 1590))

    pozyx_localizer.initialize()

    ams_device = light_sensor.LightSensor.get_device(1)
    ams_light_sensor = light_sensor.LightSensor(AMS_LIGHT_SENSOR_I2C_ADDRESS, ams_device)

    ams_light_sensor.initialize()


def start_measurement():
    while True:
        print("{0}/{1}".format(pozyx_localizer.do_positioning(), ams_light_sensor.do_measurement()))


if __name__ == "__main__":
    main()

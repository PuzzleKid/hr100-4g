import log
import utime
from machine import I2C

# Register address
NSA2862_SET_REG = 0x30
NSA2862_DATA_REG = 0x06

# Work mode
NSA2862_MODE_CONTINUE = 0x03

NSA2862_DATA_LENGHT = 0x06

# Bind it to the external interrupt pin。
class Sensor(object):
    i2c_dev = None
    address = None
    int_pin = None
    dev_log = None

    def __init__(self, slave_address = 0x6d):
        self.dev_log = log.getLogger("I2C")
        self.address = slave_address
        self.i2c_dev = I2C(I2C.I2C0, I2C.STANDARD_MODE)
        self.sensor_init()
        utime.sleep_ms(100)
        pass

    def read_data(self, regaddr, datalen, debug=False):
        r_data = [0x00 for _ in range(datalen)]
        r_data = bytearray(r_data)
        reg_addres = bytearray([regaddr])
        self.i2c_dev.read(self.address, reg_addres, 1, r_data, datalen, 1)
        ret_data = list(r_data)
        if debug is True:
            self.dev_log.debug(" read 0x{0:02x} 0x{1:02x} 0x{2:02x} from 0x{3:02x}".format(ret_data[0], ret_data[1], ret_data[2], regaddr))
        return ret_data

    def write_data(self, regaddr, data, debug=False):
        w_data = bytearray([regaddr, data])
        # Temporarily put the address to be transmitted in the data bit
        self.i2c_dev.write(self.address, bytearray(0x00), 0, bytearray(w_data), len(w_data))
        if debug is True:
            self.dev_log.debug(" write 0x{0:02x} to 0x{1:02x}".format(data, regaddr))

    def sensor_reset(self):
        pass

    def sensor_init(self):
        self.sensor_reset()  # 1. Reset the device; 2. Initialize the sensor
        self.write_data(NSA2862_SET_REG, NSA2862_MODE_CONTINUE)

    def read_press_temp(self):
        r_data = self.read_data(NSA2862_DATA_REG, NSA2862_DATA_LENGHT)

        # Convert the temperature as described in the data manual
        pressure = (r_data[0] << 16) | (
                r_data[1] << 8) | (r_data[2] )
        if (pressure&0x800000)==0x800000:
            pressure=~pressure
            pressure=pressure+1
            pressure*=-1
        pressure=pressure/8388608 -0.1 
        pressure=3125*pressure
        self.dev_log.info("current pressure is {}Kpa".format(pressure))
        temperature = (r_data[3] << 16) | (
                r_data[4] << 8) | r_data[5]
        if temperature<8388608:
            temperature=temperature/65536+25
        else :
            temperature=(temperature-16777216)/65536 +25
        self.dev_log.info("current temperature is {}°C".format(temperature))
        return pressure, temperature

if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)  # Set log output level
    sensor = Sensor()
    while True:
        sensor.read_press_temp()
        utime.sleep(1)

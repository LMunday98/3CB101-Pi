import smbus
import time
import datetime
from .data import Data

class Sensor():

    # Register
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c

    address = 0x68       # via i2cdetect

    def __init__(self, rowerId):
        self.rowerId = rowerId

        # Setup
        self.bus = smbus.SMBus(1) # bus = smbus.SMBus(0) for Revision 1

        # Activate to be able to address the module
        self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)

        self.cal_offset = [0,0]

    def read_byte(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def read_word(self, reg):
        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg+1)
        value = (h << 8) + l
        return value

    def read_word_2c(self, reg):
        val = self.read_word(reg)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def calibrate(self):
        print("Calibrating sensor...")
        calibration_data = self.get_cal_offset()
        self.cal_offset[0] = self.cal_offset[0] + calibration_data[0]
        self.cal_offset[1] = self.cal_offset[1] + calibration_data[1]
        print("Calibration offset:", self.cal_offset)

    def get_cal_offset(self):
        data_reading = self.get_data()
        data_dict = data_reading.get_data_dict()
        rx = data_dict['rx']
        ry = data_dict['ry']
        return [rx, ry]

    def get_data(self):
        gyro_readings = {
            'gx' : self.read_word_2c(0x43),
            'gy' : self.read_word_2c(0x45),
            'gz' : self.read_word_2c(0x47),
        }

        accel_readings = {
            'ax' : self.read_word_2c(0x3b),
            'ay' : self.read_word_2c(0x3d),
            'az' : self.read_word_2c(0x3f),
        }
        
        return Data(self.rowerId, gyro_readings, accel_readings, self.cal_offset, datetime.datetime.now())
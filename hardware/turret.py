import serial
import time

class Turret:
    def __init__(self, comport, baudrate=9600, timeout=3, terminator='\r'):
        self.comport = comport
        self.baudrate = baudrate
        self.timeout = timeout
        self.terminator = terminator
        self.position = 1

        self.serial_port = serial.Serial(
            port=self.comport,
            baudrate=self.baudrate,
            timeout=self.timeout
        )

    def rotate_to_position(self, pos, wait=False):
        cmd = f'cRDC{pos}{self.terminator}'
        self.serial_port.write(cmd.encode())
        
        if wait:
            msg = self.response()
            return msg == 'oRDC'
        else:
            return True

    def response(self):
        response = self.serial_port.readline().decode().strip()
        return response

    def kill(self):
        if self.serial_port.is_open:
            self.serial_port.close()


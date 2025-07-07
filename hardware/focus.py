import serial
import time

class Focus:
    def __init__(self, comport, baudrate=115200):
        self.mm_to_steps = 32000 * 5
        self.um_to_steps = 32 * 5
        self.position = 0

        self.serial_port = serial.Serial(
            port=comport,
            baudrate=baudrate,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            timeout=4
        )

    def kill(self):
        if self.serial_port.is_open:
            self.serial_port.close()

    def calculate_checksum(self, cmd):
        return sum(cmd) & 0xFF  # checksum is sum of command bytes, 8-bit

    def start_command(self, cmd_bytes, stop):
        if stop == 1:
            startcmd = [1, 3, 1, 0]
        else:
            startcmd = [1, 4, 1, 0]
        return startcmd + cmd_bytes

    def send_command(self, cmd):
        self.serial_port.write(bytearray(cmd))
        answer = self.serial_port.read(9)
        if len(answer) < 3:
            return 'No response'
        errorcode = answer[2]
        if errorcode == 1:
            return 'Checksum incorrect'
        elif errorcode == 2:
            return 'Invalid Command'
        elif errorcode == 3:
            return 'Wrong Type'
        elif errorcode == 4:
            return 'Invalid Value'
        elif errorcode == 5:
            return 'Configuration EEPROM locked'
        elif errorcode == 6:
            return 'Command not available'
        else:
            return errorcode

    def um2byte(self, dist):
        microsteps = int(abs(dist) * self.um_to_steps)
        if dist == 0:
            dir_bit = 1
        else:
            dir_bit = int((int(dist > 0)))

        if abs(dist) > 2000:  # don't allow movement if it is > 2 mm
            return [0, 0, 0, 0]
        if dir_bit == 1:
            val = microsteps
        else:
            val = (2 ** 32 - microsteps)
        # Convert to 4 bytes (big endian)
        return [
            (val >> 24) & 0xFF,
            (val >> 16) & 0xFF,
            (val >> 8) & 0xFF,
            val & 0xFF
        ]

    def rotate_relative(self, dist):
        value_bytes = self.um2byte(dist)
        cmd = self.start_command(value_bytes, stop=0)
        checksum = self.calculate_checksum(cmd)
        cmd.append(checksum)
        response = self.send_command(cmd)
        if abs(dist) <= 2000:
            self.position -= dist
        return self.position

    def get_pos(self):
        return self.position
    
    def move_to(self, target):
        if abs(self.position - target) <= 2000:
            self.rotate_relative(self.position - target)
        return self.position

    def set_zero(self):
        self.position = 0
        return self.position
    
    def home(self):
        self.rotate_relative(self.position)

    def stop(self):
        value_bytes = self.um2byte(0)
        cmd = self.start_command(value_bytes, stop=1)
        checksum = self.calculate_checksum(cmd)
        cmd.append(checksum)
        response = self.send_command(cmd)
        return response
    
    def __del__(self):
        self.serial_port.close()

# Example usage:
# fc = FocusControl()
# print(fc.rotate_relative(1.0))  # Move 1 mm
# print(fc.get_pos())
# fc.emergencystop()
# fc.kill()
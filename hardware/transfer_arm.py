from pylablib.devices import Thorlabs
import numpy as np
import time
from tqdm import tqdm

class TransferArm():
    """
    Control transfer arm x, y, and z motors
    """
    
    def __init__(self, serial_num_x, serial_num_y, serial_num_z):
        self.motors = []
        self.default_speeds= []
        try:
            self.x_motor = Thorlabs.KinesisMotor(serial_num_x, scale=True)
            self.motors.append(self.x_motor)
            self.default_speeds.append(self.x_motor.get_jog_parameters().max_velocity // 4)
        except:
            print("Could not mount X motor.")

        try:
            self.y_motor = Thorlabs.KinesisMotor(serial_num_y, scale=True)
            self.motors.append(self.y_motor)
            self.default_speeds.append(self.y_motor.get_jog_parameters().max_velocity // 4)
        except:
            print('Could not mount Y motor')
        
        try:
            self.z_motor = Thorlabs.KinesisMotor(serial_num_z, scale=True)
            self.motors.append(self.z_motor)
            self.default_speeds.append(self.z_motor.get_jog_parameters().max_velocity // 4)
        except:
            print('Could not mount Z motor')

        x_params = self.x_motor.get_jog_parameters()
        y_params = self.y_motor.get_jog_parameters()
        z_params = self.z_motor.get_jog_parameters()
        self.x_speed, self.x_accl = x_params.max_velocity, x_params.acceleration
        self.y_speed, self.y_accl = y_params.max_velocity, y_params.acceleration
        self.z_speed, self.z_accl = z_params.max_velocity, z_params.acceleration

    def set_home(self, coords=None):
        """
        Define the chip origin.  If *coords* is omitted, the current stage
        position is taken as the origin.
        """
        if coords is None:
            self.home_location = np.array(
                [
                    self.x_motor.get_position(),
                    self.y_motor.get_position(),
                    self.z_motor.get_position()
                ], 
                 dtype=float
            )
        elif len(coords) == 3:
            self.home_location = np.asarray(coords, dtype=float)
        else:
            raise TypeError("`coords` must be None or an iterable of length 3")
        
    def change_speed(self, motor, up_down):
        """
        Sets speed of motor (0, 1, 2); up_down should be either '+' or '-'
        """

        current_speed = self.motors[motor].get_jog_parameters().max_velocity
        speed_change = self.default_speeds[motor]

        if up_down=='+':
            new_speed = current_speed + speed_change
        elif up_down=='-':
            new_speed = current_speed - speed_change
        else:
            raise ValueError('Invalid parameter passed for up_down')
        
        self.motors[motor].setup_jog(max_velocity=new_speed)
        return True
    
    def get_pos(self):
        """
        Get Motor Positions
        """

        pos = []
        for motor in self.motors:
            pos.append(motor.get_position())

        return pos

    def stop(self):
        """
        Stop Motor Motion
        """
        
        for motor in self.motors:
            motor.stop(sync=False)
        
        for motor in self.motors:
            motor.wait_for_stop()

        return True
    
    def move_to(self, location, wait=False):
        """
        Moves to given location. If len(location) == 2, then will move
        x and y motors to given coordinate. If len(location) == 2, then 
        will move x, y, and z motors to given coordinate. 

        Wait will pause execution until motion is complete.
        """
        
        for i in range(len(location)):
            self.motors[i].move_to(location[i])

        if wait:
            for i in range(len(location)):
                self.motors[i].wait_for_stop()

    def move_home(self, wait=False):
        """
        Moves the stage back to home location set by set_home()
        """
        
        self.move_to(self.home_location, wait=wait)

    def jog_in_direction(self, bearing, quick_stop=True):
        '''
        Jogs stage in direction of bearing (measured in degrees counterclockwise 
        from x-axis). If quick_stop is True, the jog will automatically stop 
        after 1 second.
        '''

        bearing = np.deg2rad(bearing)

        x_factor = np.cos(bearing)
        y_factor = np.sin(bearing)

        self.x_motor.setup_jog(max_velocity=self.x_speed * abs(x_factor), acceleration=self.x_accl, mode='continuous')
        self.y_motor.setup_jog(max_velocity=self.y_speed * abs(y_factor), acceleration=self.y_accl, mode='continuous')

        if x_factor >= 0.01:
            self.x_motor.jog('+', kind='builtin')
        elif x_factor <= -0.01:
            self.x_motor.jog('-', kind='builtin')
        else:
            self.x_motor.stop(immediate=True, sync=False)

        if y_factor >= 0.01:
            self.y_motor.jog('-', kind='builtin')
        elif y_factor <= -0.01:
            self.y_motor.jog('+', kind='builtin')
        else:
            self.y_motor.stop(immediate=True, sync=False)

        if quick_stop:
            time.sleep(1)
            self.x_motor.stop(sync=False)
            self.y_motor.stop(sync=False)

    def start_manual_control(self, stop: str='esc', focus_comport: str=None, turret_comport: str=None, wasd: bool=False) -> bool:
        """
        Manually control microscope stage, focus motors, and turret.

        Args:
            stop: Key to press to stop manual mode
            wasd: If true, uses wasd control rather than arrow keys

        Returns:
            complete: True once manual control terminates properly
        """
        
        import keyboard

        prev_pos = self.get_pos()

        if wasd:
            up, down, left, right = 'w', 's', 'a', 'd'
        else:
            up, down, left, right = 'up', 'down', 'left', 'right'

        while True:
            key = keyboard.read_event()
            if key.name == stop:
                break

            if key.name == 'z':
                if key.event_type == 'up':
                    self.z_motor.stop(sync=False)
                else:
                    self.z_motor.jog('-', kind='builtin')
            
            elif key.name == 'x':
                if key.event_type == 'up':
                    self.z_motor.stop(immediate=True, sync=False)
                else:
                    self.z_motor.jog('+', kind='builtin')

            if key.name == up:
                if key.event_type == 'up':
                    self.y_motor.stop(sync=False)
                else:
                    self.y_motor.jog('-', kind='builtin')
            
            elif key.name == down:
                if key.event_type == 'up':
                    self.y_motor.stop(immediate=True, sync=False)
                else:
                    self.y_motor.jog('+', kind='builtin')

            elif key.name == left:
                if key.event_type == 'up':
                    self.x_motor.stop(immediate=True, sync=False)
                else:
                    self.x_motor.jog('+', kind='builtin')
            
            elif key.name == right:
                if key.event_type == 'up':
                    self.x_motor.stop(sync=False)
                else:
                    self.x_motor.jog('-', kind='builtin')
            
            elif key.name == 'j':
                current_pos = self.get_pos()
                print(np.array(current_pos) - np.array(prev_pos))
                prev_pos = current_pos
                time.sleep(0.25)

            elif key.name == 'J':
                current_pos = self.get_pos()
                print(np.array(current_pos) - np.array(prev_pos))
                print(f'{(current_pos[0] - prev_pos[0])/610_000} in x {(current_pos[1] - prev_pos[1])/610_000} in')
                prev_pos = current_pos
                time.sleep(0.25)

            elif key.name == 'h':
                current_pos = self.get_pos()
                print(f'Current Position: {np.array(current_pos)}')
                time.sleep(0.25)

            elif key.name == '[':
                x_speed = self.x_motor.get_jog_parameters().max_velocity
                y_speed = self.y_motor.get_jog_parameters().max_velocity
                self.x_motor.setup_jog(max_velocity=(x_speed + 1_000))
                self.y_motor.setup_jog(max_velocity=(y_speed + 1_000))
                print(self.x_motor.get_jog_parameters().max_velocity, self.y_motor.get_jog_parameters().max_velocity)
            elif key.name == ']':
                x_speed = self.x_motor.get_jog_parameters().max_velocity
                y_speed = self.y_motor.get_jog_parameters().max_velocity
                if x_speed > 1_000 and y_speed > 1_000:
                    self.x_motor.setup_jog(max_velocity=(x_speed - 1_000))
                    self.y_motor.setup_jog(max_velocity=(y_speed - 1_000))
                print(self.x_motor.get_jog_parameters().max_velocity, self.y_motor.get_jog_parameters().max_velocity)
        
        return True

if __name__ == '__main__':
    import sys

    x = '26002181'
    y = '26001655'
    z = '26001674'

    # print(Thorlabs.list_kinesis_devices())
    # x_motor = Thorlabs.KinesisMotor(x)
    # print(x_motor.get_homing_parameters())
    # y_motor = Thorlabs.KinesisMotor(y)
    # print(y_motor.get_homing_parameters())

    # x_motor.setup_jog(max_velocity=10_000_000, acceleration=70_000_000)
    # print(x_motor.get_jog_parameters())
    # print(y_motor.get_jog_parameters())
    # print(x_motor.get_position())
    # x_motor._move_by(-10000000)
    # x_motor.wait_for_stop()
    # x_motor.jog('+', kind='builtin')
    # print(x_motor.is_moving())
    # time.sleep(4)
    # print(x_motor.get_position())

    arm = TransferArm(x, y, z)
    arm.x_motor.setup_jog(step_size=100_000, max_velocity=10_000_000, acceleration=70_000_000)
    arm.y_motor.setup_jog(max_velocity=10_000_000, acceleration=70_000_000)
    arm.z_motor.setup_jog(step_size=100, max_velocity=10_000_000, acceleration=70_000_000)

    # try:
    #     x = float(sys.argv[1])
    #     y = float(sys.argv[2])
    #     y = float(sys.argv[3])
    #     arm.move_to([x, y, z])
    # except:
    #     pass

    # try:
    #     print('Starting Manual Tranfer Arm Control')
    #     print('Press q to end Manual Transfer Arm Control')
    #     if arm.start_manual_control('q', focus_comport='COM5', turret_comport='COM7', wasd=False):
    #         print('Ended manual control mode.')

    # except KeyboardInterrupt:
    #     arm.stop()
    #     print('Stopped Motion.')
    #arm = TransferArm(x, y, z)
    arm.z_motor.setup_jog(max_velocity=10_000_000, acceleration=70_000_000)
    x_now, y_now, z_now = arm.get_pos()
    z_target = z_now - 500_000
    arm.move_to([x_now, y_now, z_target], wait=True)
    print("Transfer arm moved to new position:", arm.get_pos())
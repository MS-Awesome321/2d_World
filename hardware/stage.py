from pylablib.devices import Thorlabs
from scipy.spatial.transform import Rotation as R
from focus import Focus
from turret import Turret
import numpy as np
import keyboard
import time


class Stage:
    """
    Scan a rectangular chip with a snake-like trajectory under a microscope
    using three Thorlabs Kinesis stages.
    """

    # spacing (µm) between adjacent scan rows for common objectives
    _ROW_SPACING_UM = {
        100: 255_000,   # 255 µm × 1000 for Kinesis' µm units
        50:  510_000,
        20: 1_260_000,
        10: 5_040_000,
    }

    # ------------------------------------------------------------------ #
    # Construction / setup helpers
    # ------------------------------------------------------------------ #
    def __init__(self, serial_num_x, serial_num_y, serial_num_z, magnification=20):
        self.motors = []
        self.default_speeds= []
        try:
            self.x_motor = Thorlabs.KinesisMotor(serial_num_x)
            self.motors.append(self.x_motor)
            self.default_speeds.append(self.x_motor.get_jog_parameters())
        except:
            print("Could not mount X motor.")

        try:
            self.y_motor = Thorlabs.KinesisMotor(serial_num_y)
            self.motors.append(self.y_motor)
            self.default_speeds.append(self.y_motor.get_jog_parameters())
        except:
            print('Could not mount Y motor')
        
        try:
            self.z_motor = Thorlabs.KinesisMotor(serial_num_z)
            self.motors.append(self.z_motor)
            self.default_speeds.append(self.z_motor.get_jog_parameters())
        except:
            print('Could not mount Z motor.')

        # pick the correct row spacing for the chosen objective
        try:
            self.short_edge_dist = self._ROW_SPACING_UM[magnification]
        except KeyError:
            raise ValueError(f"Unsupported objective magnification: {magnification}")

        self.mag = magnification
        self.home_location   = np.zeros(3)   # (x, y, z) in stage units (µm)
        self.rotation_matrix = np.eye(3)     # lab-frame = chip-frame at default
        self.long_edge = None                # set later in µm
        self.short_edge = None               # set later in µm

    def set_home(self, coords=None):
        """
        Define the chip origin.  If *coords* is omitted, the current stage
        position is taken as the origin.
        """
        if coords is None:
            self.home_location = np.array(
                [self.x_motor.get_position(),
                 self.y_motor.get_position(),
                 0.0], dtype=float
            )
        elif len(coords) == 3:
            self.home_location = np.asarray(coords, dtype=float)
        else:
            raise TypeError("`coords` must be None or an iterable of length 3")

    def set_direction(self, bearing_deg):
        """
        Choose the direction of the fast-scan axis: *bearing_deg* is a
        counter-clockwise angle (degrees) from +x.
        """
        self.rotation_matrix = R.from_euler("z", bearing_deg, degrees=True).as_matrix()

    def set_chip_dims(self, long_edge_mm, short_edge_mm):
        """
        Store chip dimensions in microns (Kinesis’ distance units).
        """
        self.long_edge  = long_edge_mm  * 1_000_000
        self.short_edge = short_edge_mm * 1_000_000

    def change_speed(self, motor, up_down):
        """
        Sets speed of motor (0, 1, 2); up_down should be either '+' or '-'
        """

        self.x_motor.setup_velocity

    def get_snake(self):
        if None in (self.long_edge, self.short_edge):
            raise RuntimeError("Call `set_chip_dims` before `start_snake`")

        coords = []
        n_rows = int(self.short_edge // self.short_edge_dist) + 1

        for i in range(n_rows):
            y_local = self.short_edge_dist * i

            left_local  = np.array([0,             y_local, 0], dtype=float)
            right_local = np.array([self.long_edge, y_local, 0], dtype=float)

            # even rows: left→right; odd rows: right→left
            row_pts = (left_local, right_local) if i % 2 == 0 else (right_local, left_local)

            for p in row_pts:
                p_world = self.rotation_matrix @ p + self.home_location  # element-wise add ✔
                coords.append(p_world)

        return coords

    # ------------------------------------------------------------------ #
    # Main routine
    # ------------------------------------------------------------------ #
    def start_snake(self, wait=True):
        """
        Perform the raster scan.  The Z-axis is untouched here, but you can
        sprinkle in z-moves where needed.
        """
        
        coords = self.get_snake()

        # execute the moves
        for x, y, _ in coords:       # ignore z for now
            self.x_motor.move_to(x)
            self.y_motor.move_to(y)
            if wait:
                self.x_motor.wait_for_stop()
                self.y_motor.wait_for_stop()

    # Get Motor Positions
    def get_pos(self):
        pos = []
        for motor in self.motors:
            pos.append(motor.get_position())

        return pos

    # Stop Motor Motion
    def stop(self):
        for motor in self.motors:
            motor.stop()
            motor.wait_for_stop()
        
        return True
    
    # Manually Control Motors
    def start_manual_control(self, stop='esc', focus_comport=None, turret_comport=None):
        if focus_comport:
            focus = Focus(focus_comport)

        if turret_comport:
            turret = Turret(turret_comport)

        focus_speed = 10

        while True:
            key = keyboard.read_event()
            if key.name == stop:
                break

            if key.name == 'up':
                if key.event_type == 'up':
                    self.y_motor.stop('-')
                else:
                    self.y_motor.jog('-')
            
            elif key.name == 'down':
                if key.event_type == 'up':
                    self.y_motor.stop()
                else:
                    self.y_motor.jog('+')

            elif key.name == 'left':
                if key.event_type == 'up':
                    self.x_motor.stop()
                else:
                    self.x_motor.jog('-')
            
            elif key.name == 'right':
                if key.event_type == 'up':
                    self.x_motor.stop()
                else:
                    self.x_motor.jog('+')

            if turret_comport:
                if key.name == '1':
                    turret.rotate_to_position(1)
                elif key.name == '2':
                    turret.rotate_to_position(2)
                elif key.name == '3':
                    turret.rotate_to_position(3)
                elif key.name == '4':
                    turret.rotate_to_position(4)
                elif key.name == '5':
                    turret.rotate_to_position(5)
            
            if focus_comport:
                if key.name == '=':
                    focus.rotate_relative(focus_speed)
                    time.sleep(0.01 * focus_speed)
                elif key.name == '-':
                    focus.rotate_relative(-1*focus_speed)
                    time.sleep(0.01 * focus_speed)
                elif key.name == '0':
                    focus_speed += 5
                    print(f'Focus Speed: {focus_speed}')
                elif key.name == '9':
                    focus_speed -= 5
                    print(f'Focus Speed: {focus_speed}')
        
        return True
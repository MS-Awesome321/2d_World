from pylablib.devices import Thorlabs
import numpy as np
import time


class Stage:
    """
    Control microscope stage, focus, and lens turret.
    """

    # spacing (µm) between adjacent scan rows for common objectives
    _ROW_SPACING_UM = {
        100: 2_550,   # 255 µm × 1000 for Kinesis' nm units
        50:  5_100,
        20: 16_400,
        10: 25_200,
        5: 50_400,
    }

    # ------------------------------------------------------------------ #
    # Construction / setup helpers
    # ------------------------------------------------------------------ #
    def __init__(self, serial_num_x, serial_num_y, magnification=20, test_mode = False):
        if not test_mode:
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

        # pick the correct row spacing for the chosen objective
        try:
            self.short_edge_dist = self._ROW_SPACING_UM[magnification]
        except KeyError:
            raise ValueError(f"Unsupported objective magnification: {magnification}")

        self.mag = magnification
        self.home_location   = np.zeros(2)
        self.rotation_matrix = np.eye(2)
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
                 self.y_motor.get_position()], 
                 dtype=float
            )
        elif len(coords) == 2:
            self.home_location = np.asarray(coords, dtype=float)
        else:
            raise TypeError("`coords` must be None or an iterable of length 3")

    def set_direction(self, bearing_deg):
        """
        Choose the direction of the fast-scan axis: *bearing_deg* is a
        counter-clockwise angle (degrees) from +x.
        """
        bearing_deg *= np.pi/180
        self.rotation_matrix = np.array([
                                    [np.cos(bearing_deg), -np.sin(bearing_deg)],
                                    [np.sin(bearing_deg),  np.cos(bearing_deg)]
                                ])

    def set_chip_dims(self, long_edge_mm, short_edge_mm):
        """
        Store chip dimensions in microns (Kinesis’ distance units).
        """
        self.long_edge  = long_edge_mm  * 100_000
        self.short_edge = short_edge_mm * 100_000

    def change_speed(self, motor, up_down):
        """
        Sets speed of motor (0 or 1); up_down should be either '+' or '-'
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

    def get_snake(self):
        if None in (self.long_edge, self.short_edge):
            raise RuntimeError("Call `set_chip_dims` before `start_snake`")

        coords = []
        n_rows = int(self.short_edge // self.short_edge_dist) + 1
        n_cols = int(self.long_edge // self.short_edge_dist) + 1  # Number of points along long edge

        for i in range(n_rows):
            y_local = self.short_edge_dist * i

            # Generate points spaced self.short_edge_dist apart along the long edge
            row_points = [np.array([self.short_edge_dist * j, y_local], dtype=float) for j in range(n_cols)]

            # even rows: left→right; odd rows: right→left
            if i % 2 == 1:
                row_points = row_points[::-1]

            for p in row_points:
                p_world = self.rotation_matrix @ p + self.home_location
                coords.append(p_world)

        return coords

    # ------------------------------------------------------------------ #
    # Main routine
    # ------------------------------------------------------------------ #
    def _placeholder():
        pass

    def start_snake(self, methods=[_placeholder]):
        """
        Perform the raster scan.
        """
        
        coords = self.get_snake()

        # execute the moves
        for x, y in coords:       # only x and y
            self.x_motor.move_to(x)
            self.y_motor.move_to(y)
            self.x_motor.wait_for_stop()
            self.y_motor.wait_for_stop()
            for method in methods:
                method()

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
        import keyboard
        from focus import Focus
        from turret import Turret

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
                    time.sleep(0.0075 * focus_speed)
                elif key.name == '-':
                    focus.rotate_relative(-1*focus_speed)
                    time.sleep(0.0075 * focus_speed)
                elif key.name == '0':
                    if focus_speed < 2000:
                        focus_speed += 5
                    print(f'Focus Speed: {focus_speed}')
                elif key.name == '9':
                    if focus_speed > 5:
                        focus_speed -= 5
                    print(f'Focus Speed: {focus_speed}')
        
        return True
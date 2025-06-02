from pylablib.devices import Thorlabs
from scipy.spatial.transform import Rotation as R
import numpy as np
import time

class Stage(Thorlabs.KinesisMotor):
    '''
    Built on pylablib Thorlabs motor package. Use this to perform auto-searching
    '''

    def __init__(self, serial_num_x, serial_num_y, serial_num_z, magnification):
        self.x_motor = Thorlabs.KinesisMotor(serial_num_x)
        self.y_motor = Thorlabs.KinesisMotor(serial_num_y)
        self.z_motor = Thorlabs.KinesisMotor(serial_num_z)
        self.mag = magnification
        if self.mag == 100:
            self.short_edge_dist = 255_000
        if self.mag == 50:
            self.short_edge_dist = 510_000
        if self.mag == 20:
            self.short_edge_dist = 1_260_000
        if self.mag == 10:
            self.short_edge_dist = 5_040_000


    def set_home(self, coords=None):
        if type(coords) != type(None):
            self.home_location = (self.x_motor.get_position(), self.y_motor.get_position())
        elif (type(coords) == tuple) and coords.length == 3:
            self.home_location = coords
        else:
            raise TypeError("Invalid coords entered")
        
    def set_direction(self, bearing):
        '''
        Bearing should be counterclockwise angle (degrees) starting from x-axis. 
        Represents long end of snaking motion.
        '''
        r = R.from_quat([0, 0, np.sin(bearing * np.pi/180), np.cos(bearing * np.pi/180)])
        self.rotation_matrix = r.as_matrix()

    def set_chip_dims(self, long_edge, short_edge):
        '''
        Should be in mm
        '''
        self.long_edge = long_edge * 1_000_000
        self.short_edge = short_edge * 1_000_000

    def start_snake(self):
        # Generate coordinates to move to
        coords = []

        num_rows = self.short_edge // self.short_edge_dist + 1
        for i in range(num_rows):
            if i%2 == 0:
                coord1 = (0, self.short_edge_dist * 1) + self.home_location
                coord1 = self.rotation_matrix @ coord1
                coords.append(coord1)

                coord2 = (self.long_edge, self.short_edge_dist * 1) + self.home_location
                coord2 = self.rotation_matrix @ coord1
                coords.append(coord2)
            else:
                coord2 = (self.long_edge, self.short_edge_dist * 1) + self.home_location
                coord2 = self.rotation_matrix @ coord1
                coords.append(coord2)

                coord1 = (0, self.short_edge_dist * 1) + self.home_location
                coord1 = self.rotation_matrix @ coord1
                coords.append(coord1)
        
        for coord in coords:
            self.x_motor.move_to(coord[0])
            self.y_motor.move_to(coord[1])
            self.x_motor.wait_for_stop()
            self.y_motor.wait_for_stop()
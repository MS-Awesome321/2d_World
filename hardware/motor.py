import serial


def um2byte(dist, um_to_steps = 32*5):
    """
    Converts a distance in micrometers to a 4-byte array for motor commands.

    Args:
        dist (int): Distance in micrometers.
        um_to_steps (int): Conversion factor from micrometers to steps.

    Returns:
        list: A list of 4 bytes representing the command.
    """
    microsteps = abs(dist) * um_to_steps

    if dist == 0:
        direction = 1
    else:
        direction = (1 if dist > 0 else 0)  # Convert +/-1 to 1 and 0

    if abs(dist) > 2000:  # Don't allow movement if it is > 2 mm
        return [0, 0, 0, 0]

    if direction == 1:
        value = microsteps
    elif direction == 0:
        value = (2**32 - 1) - microsteps + 1
    else:
        return [0, 0, 0, 0]

    # Convert the integer value to a 4-byte array
    byte_array = [(value >> (8 * i)) & 0xFF for i in range(4)][::-1]
    return byte_array

def start_command(stop):
    if stop:
        startcmd = [1, 3, 1, 0]
    else:
        startcmd = [1, 4, 1, 0] 
    return startcmd

##################

# value = um2byte(dist);
        
# separate binary string into four separate bytes
# cmd   = [bin2dec(value(1:8)) bin2dec(value(9:16)) bin2dec(value(17:24)) bin2dec(value(25:32))]; 

# add the beginning of the command and the checksum
# cmd = StartCommand(cmd,0);

# checksum = dec2bin(CalculateChecksum(cmd),8);
# checksum = bin2dec(checksum(end-7:end));
# cmd = [cmd checksum];

def calculate_checksum(input):
    return sum(input)

def rotate_relative(dist):
    value = um2byte(dist)
    cmd = start_command(False) + value
    checksum = calculate_checksum(cmd) & 0xFF 
    cmd.append(checksum)
    return cmd


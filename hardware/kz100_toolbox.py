# -*- coding: utf-8 -*-
"""
kz100_toolbox
-----------------
Python function library for multi-axis motor controllers using the same serial protocol
as the KZ-100.

Main features:
- SetSpeed               Continuous velocity motion
- SetMaxSpeed            Set maximum speed
- SetDistance            Move a specified distance (or microsteps)
- GetDisplay             Read current position
- GetStatus              Read limit / motion mode / home status
- SaveRecall             Save / load arbitrary speed motion data
- SetArbitraryMotionData Configure arbitrary speed motion profile
- TrigArbitraryMotion    Trigger arbitrary speed motion
- Stop                   Emergency stop all axes

Notes:
- Requires pyserial:  pip install pyserial
- All functions use fixed serial parameters: 57600, 8N1, timeout=3s
"""

import serial
from typing import Sequence


# ======================== Internal helper functions ======================== #

def _open_serial(COM_port: str, timeout: float = 3.0) -> serial.Serial:
    """
    Internal helper: open the serial port with uniform parameters.
    """
    ser = serial.Serial(
        COM_port,
        baudrate=57600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout,
        rtscts=False,
    )
    return ser


def _write_command(ser: serial.Serial, command: str) -> None:
    """
    Internal helper: send a command to the controller one character at a time,
    waiting for a 1-byte echo after each character.

    Example command: 'SX100;'
    """
    for ch in command:
        ser.write(ch.encode("ascii"))  # Python 3 requires bytes
        ser.read(1)                    # Wait for 1 byte response (usually 0x0D)


# ======================== Public API functions ======================== #

###################  Function: Set continuous speed   ###################


def SetSpeed(COM_port: str, channel: str, speed: int) -> None:
    """
    Make the motor run continuously at the specified speed.

    Parameters:
        COM_port : serial port name, e.g. 'COM1','COM2','COM3',...
        channel  : 'X', 'Y', 'Z', 'L'
        speed    : integer speed, range -16383 ~ 16383
                   Unit: (5^5 / 2^20) revolutions/second
    """
    command = f"S{channel}{speed};"

    ser = _open_serial(COM_port)
    try:
        _write_command(ser, command)
    finally:
        ser.close()


###################  Function: Set maximum running speed   ###################


def SetMaxSpeed(COM_port: str, channel: str, MaxSpeed: int) -> None:
    """
    Set the maximum running speed.

    Parameters:
        COM_port : serial port name
        channel  : 'X', 'Y', 'Z', 'L'
        MaxSpeed : maximum speed, 0 ~ 16383
                   Unit: (5^5 / 2^20) revolutions/second
    """
    command = f"M{channel}{MaxSpeed};"

    ser = _open_serial(COM_port)
    try:
        _write_command(ser, command)
    finally:
        ser.close()


###################  Function: Move motor by a specified distance   ###################


def SetDistance(COM_port: str, channel: str, distance: int) -> None:
    """
    Move the motor by a specified distance (specified revolutions / microsteps).

    Parameters:
        COM_port : serial port name
        channel  : 'X','Y','Z','L'
        distance : integer distance, range -2^30 ~ 2^30
                   Unit: 1/12800 revolutions (i.e. 1 revolution = 12800)
    """
    command = f"D{channel}{distance};"

    ser = _open_serial(COM_port)
    try:
        _write_command(ser, command)
    finally:
        ser.close()


###################  Function: Get displayed position data   ###################


def GetDisplay(COM_port: str, channel: str) -> int:
    """
    Get the displayed position data for an axis.

    Parameters:
        COM_port : serial port name
        channel  : 'X','Y','Z','L'

    Returns:
        Position data (int), parsed from the 9 characters returned by the controller.
    """
    command = f"U{channel};"

    ser = _open_serial(COM_port)
    try:
        _write_command(ser, command)
        s = ser.read(9)  # 9 characters (bytes)
    finally:
        ser.close()

    text = s.decode("ascii", errors="ignore").strip()
    return int(text)


###################  Function: Get limit / motion mode / home status   ###################


def GetStatus(COM_port: str, Content: str) -> str:
    """
    Get limit status, motion mode, or home status.

    Parameters:
        COM_port : serial port name
        Content  : 'S' —— limit status
                   'M' —— motion mode
                   'H' —— home status

    Returns:
        A single-character string (str). Bit meanings are in the manual.
    """
    command = f"U{Content};"

    ser = _open_serial(COM_port)
    try:
        _write_command(ser, command)
        s = ser.read(1)  # bytes
    finally:
        ser.close()

    return s.decode("ascii", errors="ignore")


###################  Function: Save / recall arbitrary speed motion data   ###################


def SaveRecall(COM_port: str, operation: str, DataID: int) -> None:
    """
    Save or load "arbitrary speed motion data" between controller memory and disk.

    Parameters:
        COM_port  : serial port name
        operation : 'S' —— Save
                    'R' —— Recall
        DataID    : ID of the arbitrary speed motion data
    """
    command = f"A{operation}{DataID};"

    ser = _open_serial(COM_port)
    try:
        _write_command(ser, command)
    finally:
        ser.close()


###################  Function: Configure arbitrary speed motion data   ###################


def SetArbitraryMotionData(
    COM_port: str,
    channel: str,
    total_seg: int,
    duration: Sequence[int],
    acceleration: Sequence[int],
    repeat: int,
) -> None:
    """
    Configure the timing segments, accelerations and repeat count for arbitrary speed motion.

    Parameters:
        COM_port    : serial port name
        channel     : 'X','Y','Z','L'
        total_seg   : total number of segments
        duration    : list/tuple of length total_seg with durations for each segment
                      Unit: 0.4096 ms
        acceleration: list/tuple of length total_seg with accelerations for each segment
                      Unit: (5^12 / 2^33) revolutions/second^2
        repeat      : repeat count, 0 means run once
    """
    if len(duration) != total_seg or len(acceleration) != total_seg:
        raise ValueError("duration and acceleration must have length equal to total_seg")

    ser = _open_serial(COM_port)
    try:
        # (1) Send which axis and the number of segments
        cmd = f"N{channel}{total_seg};"
        _write_command(ser, cmd)

        # (2) Send time and acceleration for each segment
        for T, A in zip(duration, acceleration):
            cmd_T = f"LT{T};"
            _write_command(ser, cmd_T)

            cmd_A = f"LA{A};"
            _write_command(ser, cmd_A)

        # (3) Send repeat count
        cmd_R = f"R{channel}{repeat};"
        _write_command(ser, cmd_R)
    finally:
        ser.close()


###################  Function: Trigger arbitrary speed motion   ###################


def TrigArbitraryMotion(COM_port: str, SumChannels: int) -> None:
    """
    Trigger the arbitrary speed motion.

    Parameters:
        COM_port    : serial port name
        SumChannels : bitmask sum of participating axes
                      X:1, Y:2, Z:4, L:8, 0 if not participating.
                      e.g.: X only -> 1; X+Y -> 3; X+Y+Z+L -> 15.
    """
    command = f"TM{SumChannels};"

    ser = _open_serial(COM_port)
    try:
        _write_command(ser, command)
    finally:
        ser.close()


###################  Function: Stop all channels immediately   ###################


def Stop(COM_port: str) -> None:
    """
    Emergency stop all axes.

    Parameters:
        COM_port : serial port name
    """
    command = "PA;"

    ser = _open_serial(COM_port)
    try:
        _write_command(ser, command)
    finally:
        ser.close()


# ======================== Official example usage (only runs when this file is executed directly) ======================== #

if __name__ == "__main__":
    # Note: This is the official example call flow. Be sure to change COM to the actual serial port on your computer!
    COM = "COM10"

    # Basic usage examples matching the manufacturer's examples

    SetDistance(COM, 'X', -1000)          # Move X motor by 1 revolution (1 rev = 12800 microsteps)
    SetDistance(COM, 'Y', -1000)         # Move Y motor by 10 revolutions 

    # SetSpeed(COM, 'X', 2013)              # X axis continuous speed ~6 rev/s
    # SetSpeed(COM, 'L', 4027)              # L axis continuous speed ~12 rev/s

    # SetMaxSpeed(COM, 'Z', 2013)           # Z axis max speed ~6 rev/s
    # SetMaxSpeed(COM, 'L', 1007)           # L axis max speed ~3 rev/s

    # print(GetDisplay(COM, 'Y'))           # Retrieve and display Y axis position
    # print(GetDisplay(COM, 'L'))           # Retrieve and display L axis position

    # print(GetStatus(COM, 'S'))            # Retrieve limit switch status
    # print(GetStatus(COM, 'M'))            # Retrieve motion mode status
    # print(GetStatus(COM, 'H'))            # Retrieve home status

    # # Configure arbitrary speed motion for X axis with 3 segments:
    # total_seg = 3
    # duration = [2441, 12207, 2441]        # ~1s, ~5s, ~1s (2441*0.4096ms≈1s, 12207*0.4096ms≈5s)
    # acceleration = [211, 0, -211]         # ~6, 0, -6 rev/s^2
    # repeat = 0                            # No repeat, run once

    # SetArbitraryMotionData(COM, 'X', total_seg, duration, acceleration, repeat)

    # # Trigger arbitrary speed motion
    # SumChannels = 1                       # Only X axis participates
    # TrigArbitraryMotion(COM, SumChannels)

    # SaveRecall(COM, 'S', 0)               # Memory -> disk, ID 0
    # SaveRecall(COM, 'R', 1)               # Disk 1 -> memory

    Stop(COM)                             # Immediately stop all axes on the controller


# if __name__ == "__main__":
#     # Note: This is the official example call flow. Be sure to change COM to the actual serial port on your computer!
#     COM = "COM10"

#     # Basic usage examples matching the manufacturer's examples

#     SetDistance(COM, 'X', 12800)          # Move X motor by 1 revolution (1 rev = 12800 microsteps)
#     SetDistance(COM, 'Y', 128000)
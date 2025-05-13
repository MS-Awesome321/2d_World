import serial
from motor import rotate_relative

s = serial.Serial('/dev/cu.usbmodemTMCSTEP1', baudrate=9600)

if s.is_open:
    print('OPEN')
else:
    print("CLOSED")

print("How many micromoters to rotate focus: ")
cmd = rotate_relative(int(input()))
print(cmd)
# [1,4,1,0,255,255,212,64,24]
s.write(bytearray(cmd))

answer = s.read(9)
int_answer = [x for x in answer]
print(int_answer)

s.close()
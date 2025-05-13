# Import necessary libraries
import win32com.client

# Initialize the control for Sample and Focus Drive
# Create the UI for Sample
fpos_sample = [100, 100, 450, 750]
f_sample = win32com.client.Dispatch("MGMotor.MGMotorCtrl.1")

# Initialize Motors of Sample
Motor_Sample_x = win32com.client.Dispatch("MGMotor.MGMotorCtrl.1")
Motor_Sample_y = win32com.client.Dispatch("MGMotor.MGMotorCtrl.1")

Motor_Sample_x.StartCtrl()
Motor_Sample_y.StartCtrl()

# Set the Serial Number for Sample Motor
SN_Sample_x = 27503936
Motor_Sample_x.HWSerialNum = SN_Sample_x
SN_Sample_y = 27503951
Motor_Sample_y.HWSerialNum = SN_Sample_y

# Identify the device
Motor_Sample_y.Identify()
Motor_Sample_x.Identify()

# Home the device
Motor_Sample_x.SetHomeParams(0, 2, 1, 0.449992, 1)
Motor_Sample_y.SetHomeParams(0, 2, 1, 0.449992, 1)
Motor_Sample_x.MoveHome(0, 0)
Motor_Sample_y.MoveHome(0, 0)

# Set the jog mode
Motor_Sample_x.SetJogMode(0, 1, 1)
Motor_Sample_y.SetJogMode(0, 1, 1)
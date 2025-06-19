from pylablib.devices import Thorlabs
import time

# Connect to motor
stage = Thorlabs.KinesisMotor("27503951")
# X: 27503936
# Y: 27503951


# Get current position (in nanometers)
pos = stage.get_position()
print(f"Current position: {pos / 1e6:.3f} mm")

# Move 2 mm down (2,000,000 nm)
target = pos + 20_000_000
stage.move_to(target)

# Wait for completion
while stage.is_moving():
    time.sleep(0.1)

print(f"Moved to {target / 1e6:.3f} mm")

# Close connection
stage.close()
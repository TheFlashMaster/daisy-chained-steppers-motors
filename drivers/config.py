# Stepper Motor (A4988 Driver)
# Connect STEP pin of A4988 to STEPPER_STEP_PIN
# Connect DIR pin of A4988 to STEPPER_DIR_PIN
# Connect ENABLE pin of A4988 (if used) to STEPPER_ENABLE_PIN (active low)
# Connect MS1, MS2, MS3 pins of A4988 as per your desired microstepping (usually hardwired)
STEPPER_STEP_PIN = 2  # GPIO17 - Step control pin
STEPPER_DIR_PIN = 3   # GPIO16 - Direction control pin
STEP_DIRECTION = -1    # Direction multiplier (-1 to reverse)
STEPPER_ZERO_OFFSET = 0  # Offset to ensure the train starts at a known position

# Stepper Motor Specifications
STEPS_PER_REVOLUTION = 200  # For a standard 1.8° stepper motor in full-step mode
DIRECTION_SETUP_DELAY_US = 10  # Microseconds to wait after setting direction before stepping
HOMING_STEP_DELAY_US = 500  # Slow step delay for accurate homing
DEFAULT_SETTLE_TIME_MS = 1000  # Milliseconds to wait for motor to settle after a move

# Motor Movement Speeds (microseconds between steps)
HOME_POSITION_SPEED = 1500      # Speed for returning to home position
TRAIN_SLOW_SPEED = 2000 # Slow speed for demo mode positioning
TRAIN_FAST_SPEED = 3000 # Fast speed for demo mode return
DEMO_POSITION_TARGET = 800      # Target position for demo mode

LIMIT_SWITCH_PIN = 0 #limit switch

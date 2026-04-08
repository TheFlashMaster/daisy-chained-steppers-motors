import utime
import machine
from config import (
    DEFAULT_SETTLE_TIME_MS,
    DIRECTION_SETUP_DELAY_US,
    STEP_DIRECTION,
    STEPPER_DIR_PIN,
    STEPPER_STEP_PIN,
    STEPPER_ZERO_OFFSET,
    LIMIT_SWITCH_PIN
)


class StepperMotorA4988:
    """
    Controls a stepper motor using an A4988 driver.

    This class handles motor movement, including moving to absolute positions
    with acceleration/deceleration ramps, and performing a homing sequence
    using a limit switch. It also integrates with an MQTT client to publish
    the motor's current position.
    """

    # --- Constants ---

    def __init__(self):
        """
        Initializes the stepper motor controller.

        Args:
            mqtt: An MQTT client instance for publishing status.
            button_pin: The machine.Pin object for the homing limit switch.
        """
        self.step_pin = machine.Pin(STEPPER_STEP_PIN, machine.Pin.OUT)
        self.dir_pin = machine.Pin(STEPPER_DIR_PIN, machine.Pin.OUT)
        
        self.button_pin = machine.Pin(LIMIT_SWITCH_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        
        self.current_position = 0  # Position in steps from the home position

    def step(self, num_steps, direction=1, delay_us=500):
        """
        Moves the motor by a specified number of steps at a constant speed.

        Args:
            num_steps (int): The number of steps to move.
            direction (int): 1 for the primary direction, -1 for the reverse direction.
            delay_us (int): Delay between step pulses in microseconds (controls speed).
        """
        # Set the direction pin. The value (0 or 1) depends on the wiring.
        # This assumes one direction is 0 and the other is 1.
        self.dir_pin.value(0 if direction == 1 else 1)
        utime.sleep_us(DIRECTION_SETUP_DELAY_US)

        # Generate step pulses
        for _ in range(abs(num_steps)):
            self.step_pin.value(1)
            utime.sleep_us(delay_us)
            self.step_pin.value(0)
            utime.sleep_us(delay_us)

    def _perform_ramp(self, num_steps, direction, start_delay_us, end_delay_us):
        """
        Performs a ramp (acceleration or deceleration) over a number of steps.

        This is achieved by linearly changing the delay between steps from a
        start delay to an end delay.

        Args:
            num_steps (int): The number of steps for this ramp phase.
            direction (int): The direction of motor rotation (1 or -1).
            start_delay_us (int): The delay for the first step in microseconds.
            end_delay_us (int): The delay for the last step in microseconds.
        """
        if num_steps <= 0:
            return

        # Handle a single step to avoid division by zero in the loop
        if num_steps == 1:
            self.step(1, direction, start_delay_us)
            return

        # Linearly interpolate the delay for each step in the ramp
        for i in range(num_steps):
            current_delay = int(
                start_delay_us
                + (end_delay_us - start_delay_us) * i / (num_steps - 1)
            )
            self.step(1, direction, current_delay)
    
    def go_to_position(self, target_position, speed):
        """
        Moves to an absolute position at a constant speed, 
        without acceleration or deceleration ramps.
        """
        # --- Parameter Validation ---
        if speed <= 0:
            raise ValueError("Speed must be positive.")

        # --- Movement Calculation ---
        steps_to_move = target_position - self.current_position
        if steps_to_move == 0:
            print(f"Already at target position: {target_position}")
            return

        # Determine direction
        direction = STEP_DIRECTION if steps_to_move > 0 else STEP_DIRECTION * -1
        abs_total_steps = abs(steps_to_move)

        # Calculate delay (inverse of speed)
        # speed is steps/sec -> delay is seconds per step half-cycle
        target_delay_us = int(1_000_000 / speed) 

        print(f"Moving from {self.current_position} to {target_position} at constant speed...")

        # --- Movement Execution ---
        # Wir rufen die existierende step-Methode auf
        self.step(abs_total_steps, direction, target_delay_us)

        # --- Finalization ---
        self.current_position = target_position
        print(f"Reached position: {self.current_position}")

        # Kurze Beruhigungszeit für die Mechanik
        utime.sleep_ms(DEFAULT_SETTLE_TIME_MS)

    def return_to_home(self, speed):
        """
        Returns the motor to its home position (zero) using a limit switch.

        The homing process is:
        1. Move slowly towards the limit switch until it is triggered.
        2. Move slowly away from the switch until it is released.
        3. Move a fixed offset distance away from the switch.
        4. Set the current position to 0.

        Args:
            speed (int): The speed (steps/sec) for the final offset move.
        """
        print("Returning to home position...")
        offset_delay_us = int(1_000_000 / speed)

        # --- 1. Move towards switch until triggered ---
        homing_direction = STEP_DIRECTION * -1  # Reverse direction for homing
        # Assumes a pull-up resistor config (button is 1 when not pressed, 0 when pressed).
        while self.button_pin.value() == 1:
            self.step(1, direction=homing_direction, delay_us=offset_delay_us)
            # We don't track position here, as it will be reset to zero later.

        print("Limit switch triggered.")

        # --- 2. Back off switch until released ---
        # Move in the opposite direction to get off the switch.
        while self.button_pin.value() == 0:
            self.step(1, direction=STEP_DIRECTION, delay_us=offset_delay_us	)

        print("Backed off limit switch.")

        # --- 3. Move to final zero offset ---
        # Move a defined number of steps away from the switch to set the final home position.
        #offset_delay_us = int(1_000_000 / speed)
        #self.step(STEPPER_ZERO_OFFSET, STEP_DIRECTION, offset_delay_us)

        # --- 4. Set logical position to zero and notify ---
        print("Home position reached and calibrated.")
        self.current_position = 0



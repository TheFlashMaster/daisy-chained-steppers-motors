from machine import UART, Pin
import utime
import neopixel
from a4988 import StepperMotorA4988
import config

class MotorArm:
    def __init__(self):
        self.uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
        
        self.n = neopixel.NeoPixel(Pin(16), 1)

        self.motor = StepperMotorA4988()
        
        self.led_color(0, 0, 0)
        print("RP2040-Zero: System ready. wating for UART-Commands...")

    def led_color(self, r, g, b):
        self.n[0] = (r, g, b)
        self.n.write()

    def run(self):
        while True:
            if self.uart.any():
                
                data = self.uart.readline()
                if data:
                    self.led_color(0, 0, 255)
                    try:
                        msg = data.decode('utf-8').strip()
                        value = msg.split(',')
                        print(f"Empfangen: '{value}'")
                        if int(value[0]) == 1: #"name" of the Motor
                            print("My turn!")
                            if value[1] == "home":
                                self.motor.return_to_home(int(value[2]))
                                self.led_color(255, 255, 0)
                            else:
                                self.motor.go_to_position(int(value[1])*16, int(value[2])) #*16 microstepping
                                self.led_color(0, 255, 0)
                        else:
                            self.led_color(255, 0, 0)
                            print("NOT my turn!")
                    except Exception as e:
                        print("Error:", e)
            

            utime.sleep_ms(100)
            self.led_color(0, 0, 255)

if __name__ == "__main__":
    mein_arm = MotorArm()
    mein_arm.run()

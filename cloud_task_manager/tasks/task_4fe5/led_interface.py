import time
import threading

class LedInterface:
    def __init__(self, led_pin:int, enable_gpio:bool=True):
        self.led_pin = led_pin
        self.is_enabled = enable_gpio
        self._is_pin_locked = False
        if enable_gpio:
            self._import_gpio_lib()
            self._configure_pin()

    def _import_gpio_lib(self):
        try:
            import RPi.GPIO as GPIO
            self.gpio = GPIO
        except Exception as e:
            print(e)
            print("Disabling GPIO")
            self.is_enabled = False

    def _configure_pin(self):
        self.gpio.setmode(self.gpio.BOARD)
        self.gpio.setup(self.led_pin, self.gpio.OUT)
        self.gpio.output(self.led_pin, self.gpio.LOW)

    def turn_off(self):
        if self.is_enabled and not self._is_pin_locked:
            self.gpio.output(self.led_pin, self.gpio.LOW)
            
    def turn_on(self):
        if self.is_enabled and not self._is_pin_locked:
            self.gpio.output(self.led_pin, self.gpio.HIGH)

    def _blink(self):
        self._is_pin_locked = True
        print("Start blink...")
        start = time.time()
        while(time.time() - start < self._duration_sec and not self._interrupt_blink):
            self.gpio.output(self.led_pin, self.gpio.HIGH)
            time.sleep(self._delay_msec/1000)
            self.gpio.output(self.led_pin, self.gpio.LOW)
            time.sleep(self._delay_msec/1000)
        self.gpio.output(self.led_pin, self.gpio.LOW)
        self._is_pin_locked = False
        print("Stop blink...")

    def blink(self, delay_msec:int, duration_sec:int=None):
        if not self.is_enabled or self._is_pin_locked:
            return
        self.t = threading.Thread(target=self._blink)
        self._delay_msec = delay_msec
        if duration_sec is None:
            self._duration_sec = 10e10
        else:
            self._duration_sec = duration_sec
        self._interrupt_blink = False
        self.t.start()

    def stop_blink(self):
        self._interrupt_blink = True

    def slow_blink(self):
        self.blink(125,1)
    
    def quick_blink(self):
        self.blink(50,1)

    def __del__(self):
        if self.is_enabled:
            self.turn_off()
            
if __name__ == "__main__":
    led = LedInterface(led_pin=12)
    led.turn_on()
    time.sleep(2)
    led.turn_off()
    time.sleep(2)
    led.blink(200)
    time.sleep(3)
    led.stop_blink()
    time.sleep(2)
    led.slow_blink()
    time.sleep(2)
    led.quick_blink()


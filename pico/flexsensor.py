'''
Using the pico as an expensive ADC.
Pico reads values from FlexForce and sends them to Pi via UART

Pico Pin 1  <--> Pi Pin 23
Pico Pin 2  <--> Pi Pin 24
Pico Pin 34 <--- FlexForce Right
'''

from machine import ADC, Pin, UART

class FlexSensor():
    GET_FLEX_VAL = b"AT+00"
    GIVE_FLEX_VAL = b"%s\r\n"
    def __init__(self, flex):
        self.flex = flex

    def get_flex_val(self, reversed=True):
        return self.flex.read_u16()
    
flex = FlexSensor(ADC(Pin(28)))
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

while True:
    cmd = uart.read(20)
    if not cmd: continue

    cmd = cmd.split(b'\r')[0]
    if cmd == FlexSensor.GET_FLEX_VAL:
        flex_val = FlexSensor.GIVE_FLEX_VAL % flex.get_flex_val()
        
        print(f"Writing val to uart: {flex_val}")
        uart.write(flex_val)

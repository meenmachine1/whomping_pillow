#!/usr/bin/env python3

import serial

class FlexComm():
    NUM_OF_SAMPLES = 100
    GET_FLEX_VAL = b"AT+00\r\n"
    ADC_MAX = 2**16
    ADC_HALF = 2**15
    def __init__(self, cal_mult=2, port="/dev/ttyAMA1", baudrate=9600, **kwargs):
        self.uart = serial.Serial(port, baudrate, **kwargs)
        self.absent_weight = self.calibrate(cal_mult)

        if self.absent_weight < 0:
            print("Could not calibrate chair. Bailing out...")
            exit(-1)

    def safe_int(val):
        try:
            return int(val)
        except ValueError as e:
            pass

        return None

    def req_val(self):
        self.uart.write(FlexComm.GET_FLEX_VAL)

    def get_val(self):
        buf = self.uart.readline()

        buf = buf.split(b"\r")

        vals = [converted for val in buf if (converted:=FlexComm.safe_int(val)) is not None]

        if not vals:
            print(f"Got no vals from sensor. Got this instead: {buf}")

        return vals[0] if vals else None

    def req_and_get_val(self):
        self.req_val()
        val = self.get_val()
        
        if val is None:
            print("Error: Was unable to get reading from pressure sensor")
        
        return val

    def someone_sitting(self, num_of_samples=1) -> bool:
        vals = []
        
        for _ in range(num_of_samples):
            val = self.req_and_get_val()

            if val is None:
                return False

            vals.append(val > self.absent_weight)        
        
        sitting = sum(vals) // len(vals)
        return bool(sitting)

    def someone_sitting_avg(self) -> bool:
        num_of_samples = 10

        vals = []
        for _ in range(num_of_samples):
            vals.append(self.someone_sitting())
        
        sitting = sum(vals) // len(vals)
        return bool(sitting)

    def calibrate(self, cal_mult) -> int:
        vals = []

        for _ in range(FlexComm.NUM_OF_SAMPLES):
            val = self.req_and_get_val()

            # print(f"Got initial value from sensor: {val}")

            if val is None or val > FlexComm.ADC_MAX:
                return -1
            
            vals.append(val)
        
        if not vals: return -1

        val = sum(vals) // len(vals)
        
        upper_limit = val * cal_mult
        if (val * cal_mult) > FlexComm.ADC_HALF:
            print("Is someone already sitting on the chair?")
            upper_limit = FlexComm.ADC_HALF
        
        if upper_limit > FlexComm.ADC_MAX:
            print(f"Calibration was greater than accuracy of ADC. Defaulting to {FlexComm.ADC_HALF}")
            upper_limit = FlexComm.ADC_HALF

        print(f"Got val {val} and got calibration: {upper_limit}")

        return upper_limit

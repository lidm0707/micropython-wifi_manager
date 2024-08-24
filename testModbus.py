
from umodbus.serial import Serial as ModbusRTUMaster
import time
import json

# RTU Host/Master setup

# the following definition is for an ESP32
rtu_pins = (17, 16)         # (TX, RX)
uart_id = 1
host = ModbusRTUMaster(
    pins=rtu_pins,          # given as tuple (TX, RX)
    baudrate=9600,        # optional, default 9600
    #data_bits=8,          # optional, default 8
    #stop_bits=1,          # optional, default 1
    #parity=None,          # optional, default None
    # ctrl_pin=12,          # optional, control DE/RE
    uart_id=uart_id         # optional, default 1, see port specific documentation
)

holding_status1 = host.read_input_registers(slave_addr=1, starting_addr=1, register_qty=2, signed=True)
holding_status2 = host.read_input_registers(slave_addr=2, starting_addr=1, register_qty=2, signed=True)

data = {
    "air": {
        "temperature": holding_status1[0],  # ค่าแรกของ holding_status1
        "humidity": holding_status1[1]      # ค่าที่สองของ holding_status1
    },
    "soil": {
        "temperature": holding_status2[0],  # ค่าแรกของ holding_status2
        "humidity": holding_status2[1]      # ค่าที่สองของ holding_status2
    }
}

# แปลงเป็น JSON string
json_string = json.dumps(data, indent=4)  # indent=4 เพื่อให้มีการจัดรูปแบบที่สวยงาม
print(json_string)














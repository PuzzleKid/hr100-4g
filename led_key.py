import utime  # 导入utime模块
from machine import Pin  # 导入Pin模块
import log  # 导入log模块
level = False
sensor_en = Pin(Pin.GPIO27, Pin.OUT, Pin.PULL_DISABLE, False)  # GPIO27配置成输出模式，默认输出0
led = Pin(Pin.GPIO32, Pin.OUT, Pin.PULL_DISABLE, False)  # GPIO27配置成输出模式，默认输出0
key = Pin(Pin.GPIO19, Pin.IN, Pin.PULL_PU, 0)
log.basicConfig(level=log.INFO)  # LOG等级为INFO
QuecPython = log.getLogger("QuecPython")  # 指定LOG对象name

while True:
    read_valu = key.read()
    print(read_valu)
    if read_valu != True:
        utime.sleep_ms(10)
        if key.read() != True:
            level = not level
            sensor_en.write(level)
            led.write(level)
            while True:
                if key.read() != False:
                    break


    utime.sleep_ms(1000)  # 延时2S

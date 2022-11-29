import utime  # 导入utime模块
import request  # 导入request模块
from machine import Pin  # 导入Pin模块
import log  # 导入log模块
g7 = Pin(Pin.GPIO32, Pin.OUT, Pin.PULL_DISABLE, 0)  # GPIO7配置成输出模式，默认输出0
log.basicConfig(level=log.INFO)  # LOG等级为INFO
QuecPython = log.getLogger("QuecPython")  # 指定LOG对象name
account = 30
while account:
    try:
        address = "www.baidu.com"
        response = request.get(address)  # 发送GET请求
        QuecPython.info("response_content: {}".format(response.content))  
        # LOG打印“响应内容的生成器对象”（具体信息如何打印见相关API介绍）
        g7.write(1)  # 写入1（输出高电平）
        QuecPython.info("GPIO7_state: {}".format(g7.read()))  # LOG打印GPIO7的电平
    except:
        g7.write(0)  # 写入0（输出低电平）
        QuecPython.info("GPIO7_state: {}".format(g7.read()))   # LOG打印GPIO7的电平
    account -= 1  # 自减
    utime.sleep(2)  # 延时2S

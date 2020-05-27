print('test')
import machine
import dht
import time
import uerrno
from machine import Pin
#35,34,39,36,

inp_gpio=[35,34,39,36,21,19,18,5,17,16,4]
input_state = [Pin(i, Pin.IN).value() for i in inp_gpio]

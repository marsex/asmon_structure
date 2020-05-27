from structure import off_sys, update
import _thread as th
from time import sleep
th_new = th.start_new_thread

def boot():
    print('\n\nStarting system\n-----------------------')
    th_new(off_sys.start,())
    print('offline system started')
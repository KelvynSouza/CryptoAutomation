import datetime
import time

__error_time = None
__error_count = 0
def check_possible_server_error():
    global __error_time
    global __error_count
    if __error_time:
        time_difference = (datetime.datetime.now() - __error_time)
        time_difference_minutes = time_difference.total_seconds() / 60
        if time_difference_minutes < 3:
            __error_count +=1
    if __error_count > 5:
        time.sleep(5)
        __error_count = 0
    __error_time = datetime.datetime.now()


for x in range(5):
    check_possible_server_error()
#coding : utf-8
import time

#time or timestamp turn to tuple/struct_time


def time_timestamp(mytime):
    #timestamp = time.time()
    #a = '2016-10-26 15:40:00'
    #timeArray = time.strptime(a,'%Y-%m-%d %H:%M:%S')
    return time.mktime(time.strptime(mytime,'%Y-%m-%d %H:%M:%S'))


def timestamp_time(mytimestamp):
    #timeArray = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(mytimestamp))

if __name__ == '__main__':
    #coupon()
    print time_timestamp('2017-03-06 15:03:41')
    #print timestamp_time(1488437541)
    #print time.localtime(1467599686)
    print timestamp_time(1488783821)
    print timestamp_time(1500434163)
    

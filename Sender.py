from time import sleep
from serial import Serial
s=Serial("COM3")
s.setRTS(0)
bitzeit = 0.2
a = ""
def send(zeichen):
    code=bin(ord(zeichen))[2:].zfill(8)
    #sleep(bitzeit)
    s.setRTS(1)
    sleep(bitzeit)
    for ziffer in code:
        s.setRTS(int(ziffer))
        sleep(bitzeit)
    s.setRTS(0)
    sleep(bitzeit)

def send_word(string):
    for i in string:
        send(i)

send_word("ABC")
s.close()

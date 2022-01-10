from time import sleep
from serial import Serial
s=Serial("COM5")
s.setRTS(0)
bitzeit = 0.2

text = 'A' 
code = ''
#bitzeit = 0.2
polling=True
while polling:
    sleep(0.001*bitzeit)
    if s.getCTS():
        polling=False
sleep(1.5*bitzeit)
for i in range(8):
    code = code+str(int(s.getCTS()))
    sleep(bitzeit)
    
text = text+chr(int(code, 2))

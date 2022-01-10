import serial.tools.list_ports

ports = serial.tools.list_ports.comports()

if len(ports) == 0:
    print("keine serielle Schnittstelle gefunden")
else:
    for port in ports:
        print (port.device)

#!/usr/bin/env python3

# model

import serial
import os

def scan():
    """
    gibt eine Liste von Strings der Namen der verfuegbaren Ports zurueck
    """
    L = []
    for i in range(10):
        try:
            s = serial.Serial('/dev/ttyS'+str(i))
            L.append(s.portstr)
            s.close()   
        except serial.SerialException:
            pass
    for i in range(10):
        try:
            s = serial.Serial('/dev/ttyUSB'+str(i))
            L.append(s.portstr)
            s.close()   
        except serial.SerialException:
            pass
    # Windows
    for i in range(256):
        try:
            s = serial.Serial('COM'+str(i))
            L.append(s.portstr)
            s.close()   
        except serial.SerialException:
            pass
    # Mac OS X
    try:
        dateinamen = os.listdir('/dev')
        for datei in dateinamen:
            if datei.find('tty.usbserial') != -1:
                s = serial.Serial('/dev/' + datei)
                L.append(s.portstr)
                s.close()
    except Exception:
        pass

    for i in range(10):
        try:
            s = serial.Serial(str(i))
            L.append(i)
            s.close()   
        except serial.SerialException:
            pass
    return L

import time, platform

def zeit():
    if platform.system() == 'Windows':
        t = time.perf_counter()
        # print('zeit: ', t)              # DEBUG
        return t
    else:
        return time.time()
    
import threading

class Model(object):
    def __init__(self):
        self.s = serial.Serial(portliste[0])
        self.s.setRTS(False)

    def setPort(self,port):
        self.s.setPort(port)
        self.s.setRTS(False)
        self.s.setDTR(False)
        
    def sendBits(self,bitmuster,bitzeit):
    
        def sende(bitmuster,bitzeit,s):
            t0 = zeit()
            n = 1
            while len(bitmuster) > 0:
                bit = bitmuster[0]
                bitmuster = bitmuster[1:]
                if bit == '1':
                    s.setRTS(True)
                else:
                    s.setRTS(False)
                while n*bitzeit > zeit() - t0:
                    time.sleep(0.001)
                n = n + 1
            s.setRTS(False)
            # print(zeit() - t0) # DEBUG

        self.sendethread = threading.Thread(target = sende, args=(bitmuster,bitzeit,self.s))
        self.sendethread.start()                
            
    def __del__(self):                                # schliesst sicher die Schnittstelle
        self.s.close()

# view

import tkinter

# zeiten = [] # DEBUG fuer Pollzeiten
    

class View(tkinter.Tk):
    def __init__(self,cbEin,cbAus,cbCTS,cbSetPort,cbHalt,cbSend):
        tkinter.Tk.__init__(self)
        # Callbacks
        self.cbEin = cbEin
        self.cbAus = cbAus
        self.cbCTS = cbCTS
        self.cbSend = cbSend
        self.cbSetPort = cbSetPort
        self.protocol("WM_DELETE_WINDOW",cbHalt)      # cbHalt wird aufgerufen, wenn das 'X' gedrueckt wird
        # Timersteuerung
        self.interval = 1                             # Pollingintervall in ms
        # 'Elektronenstrahl'
        self.enabled = True
        self.y = 30                                   # Position der Linie fuer '0'
        self.y1 = 20                                  # 'Hoehe einer 1' in Pixel
        self.x = 0                                    # aktuelles x
        self.xa = 0                                   # altes x
        self.t0 = zeit()                              # Zeit am Anfang einer Zeile
        self.t = zeit() - self.t0                     # Zeit seit Anfang einer Zeile
        self.ta = zeit()
        self.cts = self.cbCTS()
        self.pxs = 50                                # Pixel/s, int
        self.pt = 0.2                                 # Pegelzeit, float
        self.pip = self.pxs*self.pt                   # Pegelintervalllaenge in Pixel
        self.t1 = zeit() # versuchsweise zur Pollingtime
        self.dnd = False                              # Drag&Drop-Flag
        self.mouse_x = None
        self.Mouse_y = None
        # Fenster
        self.title("Pegel-Transceiver")
        self.geometry('640x480')
        # Label
        self.lP = tkinter.Label(master=self, text='Port:')
        self.lP.place(x=20, y=20)
        self.lS = tkinter.Label(master=self, text='px/s:')
        self.lS.place(x=200, y=20)
        self.lCTS = tkinter.Label(master=self, text='CTS:')
        self.lCTS.place(x=507, y=20)
        self.lPegel = tkinter.Label(master=self, text='Pegel:')
        self.lPegel.place(x=20, y=55)
        self.lPegelzeit = tkinter.Label(master=self, text='Pegelzeit:')
        self.lPegelzeit.place(x=310, y=55)
        self.ls = tkinter.Label(master=self, text='s')
        self.ls.place(x=410, y=55)
        # Optionmenu
        self.vS = tkinter.StringVar(master=self)
        self.scan = portliste
        self.vS.set(self.scan[0])
        self.oS = tkinter.OptionMenu(self,self.vS,*self.scan, command=self.cbOption)
        self.oS.place(x=60,y=14, width=120)
        # Entry
        self.eA = tkinter.Entry(master=self)
        self.eA.insert(0, str(self.pxs))
        self.eA.place(x=240, y=20, width=50)
        self.ePegel = tkinter.Entry(master=self)
        self.ePegel.insert(0, str('110010101'))
        self.ePegel.place(x=60, y=55, width=230)
        self.ePegelzeit = tkinter.Entry(master=self)
        self.ePegelzeit.insert(0, str('0.2'))
        self.ePegelzeit.place(x=370, y=55, width=40)
        # Buttons
        self.bStart = tkinter.Button(master=self, text="Start", command=self.start)
        self.bStart.place(x=300,y=14,width=60)
        self.bStop = tkinter.Button(master=self, text="Stop", command=self.stop)
        self.bStop.place(x=370,y=14,width=60)
        self.bClear = tkinter.Button(master=self, text="Clear", command=self.clear)
        self.bClear.place(x=440,y=14,width=60)
        self.bSend = tkinter.Button(master=self, text="Send", command=self.send)
        self.bSend.place(x=440,y=50,width=60)
        self.bRTS = tkinter.Button(master=self, text="RTS")
        self.bRTS.bind('<Button-1>',self.cbEin)
        self.bRTS.bind('<ButtonRelease>',self.cbAus)
        self.bRTS.place(x=570,y=14,width=60)
        # Canvases
        self.cLed = tkinter.Canvas(master=self,width=22,height=22)
        self.cLed.place(x=542,y=18)
        self.c = tkinter.Canvas(master=self,width=640,height=450)
        self.c.place(x=0,y=80)
        # Lineal
        self.Lineal()
        # LED
        self.item = self.cLed.create_oval(1,1,20,20,fill='#550000',tags=('LED'))
        # Timer starten
        self.after(0,self.poll)

    def Lineal(self):
        lx = 10
        ly = 380
        d = 3
        self.c.delete('Lineal')
        # print(self.pip) # DEBUG
        self.c.create_line(lx,ly,lx+self.pip*20,ly,fill='#ff0000',tags=('Lineal'))
        for i in range(1,20):
            self.c.create_line(lx+i*self.pip,ly-d,lx+i*self.pip,ly+d,fill='#ff0000',tags=('Lineal'))         
        self.c.tag_bind('Lineal','<Enter>',self.mouse_enter)
        self.c.tag_bind('Lineal','<Leave>',self.mouse_leave)
        self.c.tag_bind('Lineal','<Button-1>',self.mouse_button1)
        self.c.tag_bind('Lineal','<ButtonRelease 1>',self.mouse_release1)
        self.c.tag_bind('Lineal','<Motion>',self.mouse_move)

    def mouse_enter(self,e):
        self.cursor_alt = self['cursor']
        self['cursor'] = 'hand1'

    def mouse_leave(self,e):
        self['cursor'] = self.cursor_alt

    def mouse_button1(self,e):
        self.dnd = True
        self.mouse_x  = e.x
        self.mouse_y  = e.y
        # print(self.mouse_x,self.mouse_y) # DEBUG

    def mouse_release1(self,e):
        self.dnd = False

    def mouse_move(self,e):
        if self.dnd:
            xoff = e.x - self.mouse_x
            yoff = e.y - self.mouse_y
            self.c.move('Lineal',xoff,yoff)
            self.mouse_x = e.x
            self.mouse_y = e.y
        
    def poll(self):
        # Anfang DEBUG fuer Pollzeiten
        """
        t = zeit()
        tp = t-self.t1
        self.t1 = t
        zeiten.append(tp)
        """
        # Ende DEBUG fuer Pollzeiten
        if self.enabled:
            self.t = zeit() - self.t0
            self.x = self.t*self.pxs
            # print(self.t, ' ',  self.x)         # DEBUG
        if self.x > 640:       # todo: width abfragen
            self.t = 0
            self.t0 = zeit()
            self.x = 0
            self.xa = 0
            self.y = self.y + self.y1 + 10
        # Bearbeiten von Led und Canvas
        aktCTS = self.cbCTS()
        if aktCTS and not self.cts:                   # Zustand 0 --> 1
            self.cLed.itemconfig('LED',fill='#ff0000')
            if self.enabled:
                self.c.create_line(self.xa,self.y+1,self.xa,self.y - self.y1) # +1 ??
                self.y = self.y - self.y1
            self.cts = True
        elif not aktCTS and self.cts:                 # Zustand 1 --> 0
            self.cLed.itemconfig('LED',fill='#550000')
            if self.enabled:
                self.c.create_line(self.xa,self.y,self.xa,self.y + self.y1)
                self.y = self.y + self.y1
            self.cts = False
        else:                                         # Zustand unveraendert
            if (self.x - self.xa > 0.5) and self.enabled:
                self.c.create_line(self.xa,self.y,self.x,self.y)
                self.xa = self.x
        # Bearbeiten der Eingabe zu px/s
        redrawLineal = False
        eingabe = self.eA.get()
        try:
            zahl = int(eingabe)
            # print(zahl) # DEBUG
            if (zahl > 0) and (zahl != self.pxs):
                self.pxs = zahl
                self.t0 = zeit() - self.x/self.pxs
                self.t = self.x/self.pxs
                redrawLineal = True             
            elif zahl <= 0:
                self.eA.delete(0,tkinter.END)
                self.eA.insert(0,'0')
        except:
            self.eA.delete(0,tkinter.END)
            self.eA.insert(0,'0')
        # Bearbeiten der Eingabe zur Pegelzeit
        eingabe = self.ePegelzeit.get()
        try:
            zahl = float(eingabe)
            # print(zahl) # DEBUG
            if (zahl > 0) and (zahl != self.pt):
                self.pt = zahl
                redrawLineal = True
        except:
            pass
        # Pegelintervalllaenge in Pixel
        self.pip = round(self.pxs*self.pt)
        
        if redrawLineal:
            self.Lineal()
            
        # rekursiver Aufruf    
        self.after(self.interval,self.poll)                      

    def start(self):
        self.enabled = True
        self.t0 = zeit() - self.x/self.pxs
        self.t = self.x/self.pxs

    def stop(self):
        self.enabled = False

    def send(self):
        if self.cbSend != None:
            self.cbSend(self.ePegel.get(),float(self.ePegelzeit.get()))

    def clear(self):
        self.c = tkinter.Canvas(master=self,width=640,height=450)
        self.c.place(x=0,y=80)
        self.y = 30                                   # Position der Linie fuer '0'
        self.x = 0                                    # aktuelles x
        self.xa = 0                                   # altes x
        self.t0 = zeit()                              # Zeit am Anfang einer Zeile

        self.t = zeit() - self.t0                     # Zeit seit Anfang einer Zeile
        self.ta = zeit()
        self.cts = self.cbCTS()
        self.Lineal()

    def cbOption(self, wert):
        # print(wert) # DEBUG
        self.cbSetPort(wert)
        

# controller

class Controller(object):
    def __init__(self):
        self.model = Model()
        self.view = View(self.schalteEin,self.schalteAus,self.model.s.getCTS,
                         self.model.setPort,self.Halt,
                         self.model.sendBits)
        self.view.mainloop()

    def schalteEin(self,event):
        self.model.s.setRTS(True)

    def schalteAus(self,event):
        self.model.s.setRTS(False)

    def setPort(self,port):
        self.model.s.setPort(port)

    def Halt(self):                                   # Aufraeumarbeiten
        self.model.s.close()                          # Schnittstelle schliessen
        self.view.quit()                              # mainloop beenden
        self.view.destroy()                           # Fenster beseitigen

# Hauptprogramm

# Zumindest bei OS X gibt Probleme, wenn der Scan zweimal durchgefÃ¼hrt wird
# Deshalb wird die Liste beim Programmstart genau einmal erzeugt
portliste = scan()

if(len(portliste) > 0):
    c = Controller()
else:
    print('Keine serielle Schnittstelle vorhanden')

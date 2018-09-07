#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
from functools import partial
from binascii import b2a_hex, a2b_qp
from bitstring import BitArray


# debug
debug = dict(zip(('mtype','sid','lat','lon','vel','course','valid','signal'),
            ('3','4048','895959.9','1795959.9','799','359','4','15')))

order = ('mtype','sid','lat','lon','vel','course','valid','signal')
# end debug

def checksum(bitarray):
    summa = sum((octet.int for octet in bitarray.cut(8)))
    return BitArray(hex(summa))[-8:].hex.upper()

def addChecksum(msg):
    return msg+checksum(BitArray(a2b_qp(msg)))

class LabelEntry:
    def __init__(self,master,**kwargs):
        self._name = None
        print (kwargs)
        self.textvar = tk.StringVar()

        self.frame = tk.LabelFrame(master,kwargs)
        self.entry = tk.Entry(self.frame,textvariable=self.textvar,bd=3)
        self.entry.pack()

    def pack(self,**kwargs):
        self.frame.pack(kwargs)

    def get(self):
        tv = self.textvar.get()
        print (tv)
        print(self.bitstring())
        return tv

    def bitstring(self):
        pass


class VelEntry(LabelEntry):
    def bitstring(self):
        return '{:03b}{:07b}'.format( *divmod(int(self.textvar.get()),100))


class CourseEntry(LabelEntry):
    def bitstring(self):
        return '{:02b}{:07b}'.format(*divmod(int(self.textvar.get()),100))


class MessageTypeEntry(LabelEntry):
    def bitstring(self):
        return '{:02b}'.format(int(self.textvar.get()))


class SonataIdEntry(LabelEntry):
    def bitstring(self):
        return '{:012b}'.format(int(self.textvar.get()))

class SignalEntry(LabelEntry):
    def bitstring(self):
        return '{:04b}'.format(int(self.textvar.get()))

class NavdataEntry:
    '''для генерализцаии LatitudeEntry и LongetudeEntry'''
    pass


class LatitudeEntry:
    def __init__(self,master,**kwargs):
        print ('LatitudeEntry:',kwargs)

        self.dd = tk.IntVar()
        self.mm = tk.IntVar()
        self.ss_s = tk.DoubleVar()
        self.ns = tk.BooleanVar()

        self.dd.set(89)
        self.mm.set(59)
        self.ss_s.set(59.9)
        self.ns.set(True)

        self.frame = tk.LabelFrame(master, kwargs)
        self.dd_entry = tk.Entry(self.frame,textvariable=self.dd,width=3,bd=2)
        self.mm_entry = tk.Entry(self.frame,textvariable=self.mm,width=3,bd=2)
        self.ss_s_entry = tk.Entry(self.frame,textvariable=self.ss_s,width=4,bd=2)

        self.ns_n = tk.Radiobutton(self.frame,text='N',variable=self.ns, value=True)
        self.ns_s = tk.Radiobutton(self.frame,text='S',variable=self.ns, value=False)

        self.dd_entry.pack(side='left')
        self.mm_entry.pack(side='left')
        self.ss_s_entry.pack(side='left')

        self.ns_s.pack(side='right')
        self.ns_n.pack(side='right')


    def pack(self,**kwargs):
        self.frame.pack(kwargs)

    def get(self):
        print( str(self.dd.get()) + str(self.mm.get()) + str(self.ss_s.get()))
        self.bitstring()
        return str(self.dd.get()) + str(self.mm.get()) + str(self.ss_s.get())

    def bitstring(self):
        bitstring = '{:07b}{:07b}{:07b}{:04b}'.format(
                self.dd.get(),
                self.mm.get(),
                *map( int, str(self.ss_s.get()).split('.') )
                )
        print (bitstring)
        return bitstring



class LongetudeEntry:
    def __init__(self,master,**kwargs):
        print ('LongetudeEntry:',kwargs)

        self.dd = tk.IntVar()
        self.mm = tk.IntVar()
        self.ss_s = tk.DoubleVar()
        self.ns = tk.BooleanVar()

        self.dd.set(179)
        self.mm.set(59)
        self.ss_s.set(59.9)
        self.ns.set(True)

        self.frame = tk.LabelFrame(master, kwargs)
        self.dd_entry = tk.Entry(self.frame,textvariable=self.dd,width=3,bd=2)
        self.mm_entry = tk.Entry(self.frame,textvariable=self.mm,width=3,bd=2)
        self.ss_s_entry = tk.Entry(self.frame,textvariable=self.ss_s,width=4,bd=2)

        self.ns_n = tk.Radiobutton(self.frame,text='W',variable=self.ns, value=True)
        self.ns_s = tk.Radiobutton(self.frame,text='E',variable=self.ns, value=False)

        self.dd_entry.pack(side='left')
        self.mm_entry.pack(side='left')
        self.ss_s_entry.pack(side='left')

        self.ns_s.pack(side='right')
        self.ns_n.pack(side='right')

    def pack(self,**kwargs):
        self.frame.pack(kwargs)

    def get(self):
        print( str(self.dd.get()) + str(self.mm.get()) + str(self.ss_s.get()))
        self.bitstring()
        return str(self.dd.get()) + str(self.mm.get()) + str(self.ss_s.get())

    def bitstring(self):
        bitstring = '{:08b}{:07b}{:07b}{:04b}'.format(
                self.dd.get(),
                self.mm.get(),
                *map( int, str(self.ss_s.get()).split('.') )
                )
        print(bitstring)
        return bitstring


class ValidEntry:
    def __init__(self,master,**kwargs):
        self.av = tk.BooleanVar()
        self.av.set(True)

        self.frame = tk.LabelFrame(master,kwargs)
        self.av_a = tk.Radiobutton(self.frame, text='A',variable=self.av, value=True)
        self.av_v = tk.Radiobutton(self.frame,text='V',variable=self.av,value=False)

        self.av_v.pack(side='right')
        self.av_a.pack(side='right')

    def pack(self,**kwargs):
        self.frame.pack(kwargs)

    def get(self):
        return str(int(self.av.get()))


class DataEntries:
    def __init__(self, master):
        self.frame = tk.Frame(master,highlightbackground="red", highlightcolor="red", highlightthickness=2, bd= 2)

        self.entryes = {'mtype': MessageTypeEntry(self.frame,text='MessageType(2bit)' ,width=19),
                        'sid': SonataIdEntry(self.frame,text='ID(12bit)'),
                        'lat': LatitudeEntry(self.frame,text='Lat(25bit) ddmmss.s'),
                        'lon': LongetudeEntry(self.frame,text='Lon(26bit) dddmmss.s'),
                        'vel': VelEntry(self.frame,text='Vel(10bit)'),
                        'course': CourseEntry(self.frame,text='Course(9bit)'),
                        'valid': ValidEntry(self.frame,text='(A)ctual / In(V)alid'),
                        'signal': SignalEntry(self.frame,text='Signal level 0..15')
                        }

        #debug:==================
        for k in filter(lambda k:k not in ('lat','lon','valid'), self.entryes.keys()):
            self.entryes[k].textvar.set(debug.get(k,'Empty'))
        #end debug ===============

        for key in order:
            self.entryes[key].pack(side='top',fill='both',expand=True)

    def pack(self,**kwargs):
        self.frame.pack(kwargs)

    def get_value(self, key, default=None):
        return self.entryes.get(key,default)

    def get(self):
        #sonata.foo()
        s = ''.join([ ''.join( e.get().split('.') ) for e in (self.entryes.get(k) for k in order) ])
        return b2a_hex(a2b_qp(s))

    def _state(self):
        ns = str(int(self.entryes['lat'].ns.get()))
        ew = str(int(self.entryes['lon'].ns.get()))
        av = self.entryes['valid'].get()
        print('av='+av+ ' ns='+ ns +' ew=' + ew)
        print( av+ns+ew)
        return '100'


    def message(self):
        # TODO: quick and dirty solution. Refact it.
        mtype = BitArray(bin=self.entryes['mtype'].bitstring())
        sid = BitArray(bin=self.entryes['sid'].bitstring())
        lat = BitArray(bin=self.entryes['lat'].bitstring())
        lon = BitArray(bin=self.entryes['lon'].bitstring())
        vel = BitArray(bin=self.entryes['vel'].bitstring())
        course =  BitArray(bin=self.entryes['course'].bitstring())
        state =  BitArray(bin=self._state())
        tail = BitArray(17) # Датчики и каналы управления игнорируются плагином.
        signal = BitArray(bin=self.entryes['signal'].bitstring())

        bs_data = mtype+sid+lat+lon+vel+course+state+tail+signal
        bs_msg = bs_data.hex.upper()

        return str('$'+ addChecksum(bs_msg) + '\n')






class Presets:
    def __init__(self,master,ebox,lentry):
        self.frame = tk.LabelFrame(master,
                                   text="Presets",
                                   highlightbackground="violet", highlightthickness=2, bd= 3,)
        self.preset = tk.Button(self.frame,command=partial(ebox.insert_from,lentry),
                                text="Not Empemented yet.",width=18,height=2,bg='gray',
                                fg='black',bd=3)

        self.preset.pack()

    def pack(self,**kwargs):
        self.frame.pack(kwargs)


class LogBox:
    def __init__(self,master):
        self.frame = tk.LabelFrame(master,text='Log:',highlightbackground="blue",highlightcolor="blue", highlightthickness=2, bd= 2)
        self.logbox = tk.Text(self.frame,font='Arial 14',wrap='word',bd = 3,height=30)

        self.logbox.pack(side='top')

        self.logbox.insert('1.0','Not emplemented yet\n')

    def pack(self,**kwargs):
        self.frame.pack(kwargs)


class EditBox:
    def __init__(self,master):
        self.frame = tk.LabelFrame(master,text='Editable BaseStation package:',highlightbackground="yellow", highlightthickness=2)
        self.editbox = tk.Text(self.frame,font='Arial 14',wrap='word',bd=3,height=2)

        self.editbox.pack(side='top')

    def pack(self,**kwargs):
        self.frame.pack(kwargs)

    def insert(self,chars='',*args):
        print(chars.encode())
        self.editbox.delete('1.0','end')
        self.editbox.insert('1.0',repr(chars),args)

    def insert_from(self, source=None,*args):
        #chars = source.get()
        chars = source.message()
        self.insert(chars)


class MainWindow:
    def __init__(self,master):
        self.lframe = tk.Frame(master,highlightbackground='green', highlightthickness=2, bd= 2)
        self.rframe = tk.Frame(master,highlightbackground='orange', highlightthickness=2, bd= 2)

        self.edit_box = EditBox(self.rframe)

        self.data_entries = DataEntries(self.lframe)
        self.data_entries.pack(side='top')

        self.presets = Presets(self.lframe,self.edit_box,self.data_entries)
        self.presets.pack(side='top',fill='both')
        self.lframe.pack(side='left',fill='y')


        #self.edit_box = EditBox(self.rframe)
        self.edit_box.pack(side='top',expand=False)
        self.log_box = LogBox(self.rframe)
        self.log_box.pack(side='top',expand=False)

        self.rframe.pack(side='left',fill='none')

    def foo():
        pass



if __name__ == '__main__':
    root = tk.Tk()
    sonata = MainWindow(root)
    root.mainloop()
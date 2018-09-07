#!/usr/bin/env python3
# -*- coding = utf-8 -*-

from bitstring import BitArray, Bits
from binascii import a2b_qp


if __name__ == '__main__':


    bits_only = Bits(int=90, length=8)
    bits_only_2 = Bits(int=60, length=7)
    bar_mtype_bin = BitArray(bin = '11')      # тип сообщения: 00 - нав.данные, 01 - текст Ж
    hex_num = hex(3)
    hex_num_str = str(hex_num)
    bar_mtype_hex = BitArray(hex_num_str)  # тип сообщения: 00 - нав.данные, 01 - текст Ж
    int_val=90
    barr_int_val = BitArray(int_val, length=9)



    mtype = BitArray(bin='11')
    sonata_id = BitArray(bin='000000000001')# id
    lat = BitArray(bin=''.join(( '1011001','0111011','0111011','1001'))) # 89,59,59,9
    #                             1011001   0111011   0111011   1001
    lon = BitArray(bin="".join(('10110011','0111011','0111011','1001'))) #179,59,59,9
    #                            10110011   0111011   0111011   1001
    vel = BitArray(bin=''.join(('111','1100011')))                       # 7,99
    #                            111   1100011
    course =  BitArray(bin=''.join(('11','0111011'))) # 3,59
    #                                11   0111011
    state =  BitArray(bin='100') # A(ctual), N(orth), E(ast)
    tail = BitArray(17) # Датчики и каналы управления игнорируются плагином.

    
    bs_data = mtype+sonata_id+lat+lon+vel+course+state+tail
    bs_msg = bs_data.hex.upper()
    print (bs_msg)



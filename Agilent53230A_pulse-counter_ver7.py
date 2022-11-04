#!/usr/bin/env python
# coding: utf-8

# # pulse counting by python
# ### K. Koike
# ### updated 2022/9/15
# 

# In[1]:


import pyvisa
import datetime
import time
#ResourceManagerはPCと計測器をつなぐクラス
rm = pyvisa.ResourceManager()
print(rm.list_resources())


# In[2]:


inst = rm.open_resource('USB0::0x0957::0x1907::MY50001169::INSTR')
inst.timeout = 20000
#.query は、オシロスコープに NI-VISA コマンドを送信し、戻り値を要求
print(inst.query('*IDN?'))


# In[3]:


#初期設定
#DC coupling
def coupling(channel, AC_DC):
    inst.write(f'INPut{channel}:COUPling {AC_DC}')
    print(f'カップリング：' + inst.query(f'INPut{channel}:COUPling?'))


# In[4]:


#Impedance setting at 50ohm
def impedance(channel, imp_set):
    inst.write(f'INPut{channel}:IMPedance {imp_set}')
    print(f'インピーダンス：' + inst.query(f'INPut{channel}:IMPedance?'))


# In[5]:


#Threshold voltage setting
def level_auto(channel, ON_OFF):
    inst.write(f'INPut{channel}:LEVel:AUTO {ON_OFF}')

def level_threshold(channel, th_percent):
    inst.write(f'INPut{channel}:LEVel:RELative {th_percent}')

def level_voltage(channel, voltage):
    inst.write(f'INPut{channel}:LEVel1:ABSolute {voltage}')


# In[33]:


#Configure totalize:time
def count(): #freq: 事前に計測した繰り返し周波数
    gate_time = 10 #1secずつカウント
    #10秒間での合計パルス数を数える
    #total_cnt = inst.query(f'MEASure:TOTalize:TIMed? {gate_time}, (@{channel})') #これだとうまくいかない。
    inst.write(f'CONFigure:TOTalize:TIMed {gate_time}, (@{channel})')
    level_auto(channel, "ON")
    inst.write('INITiate:IMMediate')
    total_cnt = float(inst.query('FETCh?'))
    return total_cnt

def measure_pulsemiss(total_cnt): #calculation of pulse missing rate
    pulse_miss = abs(freq - total_cnt/10)
    if pulse_miss < 500:
        decision = 'Very good'
    elif pulse_miss < 10000:
        decision = 'OK'
    else:
        decision = 'NG'
    print(f'パルス抜け: {pulse_miss}　cnt/sec => {decision}')
    return [freq, total_cnt, pulse_miss, decision]


# In[27]:


#測定データの書き込み
#file_name: ファイルの名前
#pulse miss: 書き込むデータ
#i: データの番号 or 経過時間
def write_txt(file_name, i, t, pulse_miss):
    with open(f'{file_name}.txt', 'a') as f: #書き込んでいくので'a'
        f.write(f'{i}, {t}, {pulse_miss}\n')


# In[34]:


''' 
set parameters
coupling : DC
impedance : 50ohm
level : auto off, 0.02V (seed 4A)
'''
channel = 1
dc = "DC"
coupling(channel, dc)

imp_set = 50 #Ohm
impedance(channel, imp_set)

level_auto(channel, "ON")
#level_auto(channel, "OFF")

#voltage = 0.01 #(V)
#level_voltage(channel, voltage)
#測定開始と同時にauto level off, threshold 50% offになるので使えない。
#th_percent = 50 #percent
#level_threshold(channel, th_percent)


# In[35]:


''' 
set measurement time and frequency
hours : measurement time in hours
frequency : pulse repetition rate measured in advance
'''
hours = 200 #測定時間 (h)
cycle = hours * 60 * 6 #number of measurement
freq = 99999818 #Define your pulse repetition rate
file_name = 'test' #Define your txt. file name

''' 
start measurement
'''
j = 0
t_elapsed = 0
while j < cycle:
    t1 = time.time() #sec
    total_cnt = count()
    t2 = time.time() #sec
    pulse_miss = measure_pulsemiss(total_cnt)
    pulse_miss = str(pulse_miss)[1:-1] #str() 関数を用いてリストを文字列に変換し、この文字列から角括弧の最初と最後の文字を削除
    t_elapsed += t2 - t1
    write_txt(file_name, j+1, t_elapsed, pulse_miss) #データをtxtに順次書き込んでいく
    j += 1


# In[ ]:





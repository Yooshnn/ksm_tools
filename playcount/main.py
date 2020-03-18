import os
import math
from pathlib import Path

spath = Path.cwd() / 'score'
rpath = Path.cwd() / 'score' / 'playcount.txt'

sfilelist = [] 
pclist = []

# input *.ksc -> sfilelist

def UPDATE__sfilelist(sfp):
    for p in Path(sfp).iterdir():
        if p.is_file(): 
            ext = (str(p)).split('.')[-1]
            if ext == ('ksc'):
                sfilelist.append(p)
        else:
            UPDATE__sfilelist(p)

# input *.ksc Data -> pclist

def UPDATE__pclist():
    """Rate, MirrorRandom, ?, BT, FX, LASER=Score, ?, ?, Gauge, ?, Playcount, Clearcount, UC, PUC"""
    for p in sfilelist:
        f = open(p, "r")
        for i in f.readlines():
            playcount = int(i.split(',')[10])
            pclist.append(playcount)
    f.close()

# calculate the result (full playcount)

def CALC():
    fc = 0
    for i in pclist:
        fc += int(i)
    return fc

# output playcount

def OUTPUT(no):
    f = open(rpath , "w")
    f.write(str(no))
    f.close()

def run():
    UPDATE__sfilelist(spath)
    UPDATE__pclist()
    OUTPUT(CALC())

run()

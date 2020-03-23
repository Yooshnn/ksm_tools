import os
import math
import chardet
import json
from pathlib import Path

config = Path.cwd() / 'config.ini'
f = open(config, 'rt', encoding="UTF-8")
for i in f.readlines():
    if i.split(":")[0] == "project":
        project = i.split(":")[1]
    
os.chdir("..")
userscorepath = Path.cwd() / 'score'
usersongpath = Path.cwd() / 'songs'
os.chdir(project)

userscorepath_username = userscorepath


scorepathlist = [] # path type
songpathlist = []
datalist = []
toplist = []

datadict = []

legacyplaycount = 0


def refresh():
    del scorepathlist[:] 
    del songpathlist[:]
    del datalist[:]
    del toplist[:]

# input songpathlist
def UPDATEsongpath(_filepath): # init with usersongpath
    for p in Path(_filepath).iterdir():
        if p.is_file():
            ext = (str(p)).split('.')[-1]
            if ext == ('ksh'):
                songpathlist.append(p)
        else:
            UPDATEsongpath(p)

# generate scorepathlist using songpathlist (discards unexisting or removed songs)
def UPDATEscorepath(_filepath): # init with userscorepath
    for p in Path(_filepath).iterdir():
        if p.is_dir(): # get username
            userscorepath_username = p # ./score/username/
            break
    
    baselen = len(str(usersongpath)) + 1 # root directories
    for p in songpathlist:
        fdir = str(p)[baselen:]
        temp = (str(userscorepath_username) + "/" + fdir)[:-1] + 'c'
        scorepathlist.append(Path(temp))
        
# ignore songpath without score
def UPDATEpath():
    UPDATEsongpath(usersongpath)
    UPDATEscorepath(userscorepath)
    
    count = 0
    unexistingindex = []
    for p in scorepathlist:
        if not Path.exists(p):
            unexistingindex.append(count)
        count += 1
    
    count = 0
    for i in unexistingindex:
        songpathlist.pop(i - count)
        scorepathlist.pop(i - count)
        count += 1

# generate data
def UPDATEdata():
    # [rate, score, grade, force, title, artist, effect, difficulty, level, playcount]
    # --------------------------^ 
    
    i = -1
    while i < len(scorepathlist) - 1:
        i += 1
        data = ["failed", 0, "D", 0, "title", "artist", "effector", "difficulty", 0, 0]
        
        # scorepath
        f = open(Path(scorepathlist[i]), 'rt', encoding="UTF-8")
        scoredata = ["failed", 0, "D", 0] # read every lines then update best
        
        for line in f.readlines():
            tempdata = ["failed", 0, "D", 0] # rate, score, grade, force
            tempdata[0] = rate(line)
            tempdata[1] = int(line.split("=")[1].split(",")[0])
            
            scoredata = list(UPDATEbestscore(line, scoredata, tempdata))
        data[0] = str(scoredata[0])
        data[1] = int(scoredata[1])
        data[2] = getgrade(data[1])
        data[9] = int(line.split(",")[10])
        f.close()
        
        
        # songpath
        f = open(Path(songpathlist[i]), 'rt', encoding=getencoding(Path(songpathlist[i])))
        songdata = ["title", "artist", "effector", "difficulty", 0]
        for line in f.readlines():
            if len(line.split("=")) > 1:
                l = line.split("=")[0]
                r = line.split("=")[1]
                if l == "title":
                    songdata[0] = str(r)[:-1]
                elif l == "artist":
                    songdata[1] = str(r)[:-1]
                elif l == "effect":
                    songdata[2] = str(r)[:-1]
                elif l == "difficulty":
                    songdata[3] = str(r)[:-1]
                elif l == "level":
                    songdata[4] = int(r)
            
        data[4] = songdata[0]
        data[5] = songdata[1]
        data[6] = songdata[2]
        data[7] = songdata[3]
        data[8] = songdata[4]
        
        data[3] = getforce(data)
        
        datalist.append(data)
                
def rate(line): # pass a line
    divl = line.split("=")[0].split(",")
    divr = line.split("=")[1].split(",")
    if divl[3] == "on" and divl[4] == "on" and divl[5] == "on": # BT FX Laser ON
        if int(divr[6]) > 0: # Clearcount > 0
            if str(divr[8]) == "1":
                return "PUC"
            if str(divr[7]) == "1":
                return "UC"
            return divl[0] # normal hard
    return "failed"

def UPDATEbestscore(line, orig, temp):
    ret = [orig[0], orig[1], "D", 0]
    
    # rate
    if temp[0] == "PUC":
        ret[0] = temp[0]
    elif temp[0] == "UC":
        if orig[0] != "PUC":
            ret[0] = temp[0]
    elif str(temp[0]) == "hard":
        if orig[0] != "PUC" and orig[0] != "UC":
            ret[0] = temp[0]
    elif temp[0] == "normal":
        if orig[0] == "failed":
            ret[0] = temp[0]
            
    # score
    if int(temp[1]) >= int(orig[1]):
        divl = line.split("=")[0].split(",")
        if divl[3] == "on" and divl[4] == "on" and divl[5] == "on": # BT FX Laser ON
            ret[1] = int(temp[1])
    
    return ret
    
def getgrade(score):
    if score > 9900000:
        return "S"
    elif score > 9800000:
        return "AAA+"
    elif score > 9700000:
        return "AAA"
    elif score > 9600000:
        return "AA+"
    elif score > 9500000:
        return "AA"
    elif score > 9300000:
        return "A+"
    elif score > 9000000:
        return "A"
    elif score > 8700000:
        return "B"
    elif score > 7500000:
        return "C"
    else:
        return "D"

def getforce(data): #[rate, score, grade, force, title, artist, effect, difficulty, level]
    ret = 1
        
    ret *= data[8] * 2
    ret *= data[1] / 10000000
    ret *= clearcoef(data[0])
    ret *= gradecoef(data[2])
    
    ret = math.floor(ret * 10000) / 10000.0
    
    return ret

def clearcoef(c):
    if c == "PUC":
        return 1.10
    elif c == "UC":
        return 1.05
    elif c == "hard":
        return 1.02
    elif c == "normal":
        return 1.00
    elif c == "failed":
        return 0.50
    
def gradecoef(g):
    if g == "S":
        return 1.05
    elif g == "AAA+":
        return 1.02
    elif g == "AAA":
        return 1
    elif g == "AA+":
        return 0.97
    elif g == "AA":
        return 0.95
    elif g == "A+":
        return 0.91
    elif g == "A":
        return 0.88
    elif g == "B":
        return 0.85
    elif g == "C":
        return 0 # no data
    else:
        return 0

# misc 
def getencoding(path): # path
    count = 0
    testStr = b''
    with open(path, 'rb') as x:
        line = x.readline()
        while line and count < 30:  #Set based on lines you'd want to check
            testStr = testStr + line
            count = count + 1
            line = x.readline()
    if chardet.detect(testStr).get('encoding') == "UTF-8-SIG":
        return "UTF-8-SIG"
    else:
        return "SHIFT_JIS"

# 
def CALC__playcount():
    fc = 0
    for i in datalist:
        fc += int(i[9])
    return fc

# SDVX V-ish force
def CALC__sdvx_v():
    for data in datalist:
        if len(toplist) < 50:
            toplist.append(data)
        else:
            for i in range(0, 50):
                if (toplist[i][3] < data[3]):
                    toplist.pop(i)
                    toplist.append(data)
                    break
    toplist.sort(key=lambda x: x[3])
    toplist.reverse()


print("successfully initialized")
print("scanning data...")
refresh()
UPDATEpath()
UPDATEdata()
CALC__playcount()
CALC__sdvx_v()


##############################
##CALCULATE LEGACY PLAYCOUNT##
##############################

PC__spathlist = [] 
PC__pclist = []

# input *.ksc -> sfilelist
def PC__UPDATEspathlist(sfp):
    for p in Path(sfp).iterdir():
        if p.is_file(): 
            ext = (str(p)).split('.')[-1]
            if ext == ('ksc'):
                PC__spathlist.append(p)
        else:
            PC__UPDATEspathlist(p)

# input *.ksc Data -> PC__pclist
def PC__UPDATEpclist():
    """Rate, MirrorRandom, ?, BT, FX, LASER=Score, ?, ?, Gauge, ?, Playcount, Clearcount, UC, PUC"""
    for p in PC__spathlist:
        f = open(p, "r")
        for i in f.readlines():
            playcount = int(i.split(',')[10])
            PC__pclist.append(playcount)
    f.close()

# calculate the result (full playcount)
def PC__CALC():
    fc = 0
    for i in PC__pclist:
        fc += int(i)
    return fc

# output playcount

PC__UPDATEspathlist(userscorepath)
PC__UPDATEpclist()
legacyplaycount = PC__CALC()


print("done.")

print("creating data.json...")
# outputs
def outputjson(data):
    sdvxvf = []
    for i in data:
        temp = dict(title=i[4], level=i[8], rate=i[0],
                     grade=i[2], score=i[1], force=i[3],
                     artist=i[5], effector=i[6], difficulty=i[7],
                     playcount=i[9])
        sdvxvf.append(temp)
    info = dict(vf_sdvx_v=sdvxvf, playcount=CALC__playcount(), legacyplaycount=legacyplaycount)
    output = dict(payload=info)
    with open("data.json", "w") as f:
        json.dump(output, f)
        
outputjson(datalist)
print("done.")
print("* Success *")
os.system("Pause")

# Imports go at the top
from microbit import *
import radio
import music
versionToken="pct"
messageBusMax=9 #min is 0, one digit avoids scrolling
roleWeight={"A":1,"B":2}
roleCounterMax={"A":3,"B":6}

roleDesc={"A":"perceptron input, weight:{}".format(roleWeight["A"]),
     "B":"perceptron input, weight:{}".format(roleWeight["B"]),
     "Z":"perceptron output, activation function: a+b>4",}

roleList=list(roleDesc.keys())

validOriginRolesPerDestination={"A":list(),
     "B":list(),
     "Z":("A","B")}

#
# this node's defeault config
#
currentRole=roleList[0]
messageBus=0

def errorHandler(halt=False,errorCode=0,desc="desc"):
    if halt:
        _="FATAL"
    else:
        _="WARN"
    print(_+":{}:{}".format(errorCode,desc))
    while True:
        display.show(errorCode)
        sleep(200)
        display.show(Image.SAD)
        sleep(2000)
        if not halt:
            break


class modelCls():
    """
    perceptron. two inputs, possibly n-fold input some day
    
    """
    def __init__(self,role,pktIn,pktOut):
        if role in roleList:
            self.role=role
            self.counter={"A":0,"B":0}
            self.out=0
            self.pktIn=pktIn
            self.pktOut=pktOut
            self.outThreshold=7
        else:
            errorHandler(halt=True, errorCode=1, desc="FATAL:unexisting role {}".format(role))
            
    def eventHandler(self,event,paramDict):
        if event=="message":
            #todo: validation
            self.message(paramDict)
        elif event=="button":
            #todo: validation
            self.button(paramDict)
            pass
        else:
            errorHandler(halt=True, errorCode=1, desc="FATAL:unexisting event {}".format(event))        

            
    def updateOutput(self):
        prevOut=self.out
        counters_sum=self.counter["A"]+self.counter["B"]
        if counters_sum >=self.outThreshold:
            self.out=1
            if  self.out!=prevOut:
                music.pitch(frequency=500,duration=250,wait=False)
        else:
            self.out=0
            if  self.out!=prevOut:            
                music.pitch(frequency=7000,duration=500,wait=False)
        display.show(counters_sum)
        for _ in range(5):
            display.set_pixel(4,_,9*self.out)

            

    
    def message(self,paramDict):
        if self.role=="Z":
            if paramDict["origin"] in self.counter.keys():
                try:
                    self.counter[paramDict["origin"]]=int(paramDict["payload"])
                    self.updateOutput()
                except Exception as e:
                    print("DEBUG:{}:model.message():{}".format(self.role,e))        
            else:
                print("WARN:{}:model.message():paramDict[origin] '{}' not in self.counter.keys".format(self.role,paramDict["origin"]))
        
        else:
            print("DEBUG:{}:model.message():unimplemented message handler".format(self.role,))
            pass

    def button(self,paramDict):
        if self.role in ("A","B"):
            increment=1
            increment*=roleWeight[self.role] #apply perceptron input's weight parameter
            if paramDict["button"]=="a":
                if self.counter[self.role]+increment > roleCounterMax[self.role]:
                    increment=0
                else:
                    self.counter[self.role]+=increment
            elif paramDict["button"]=="b":
                if self.counter[self.role]-increment < 0:
                    increment=0
                else:
                    self.counter[self.role]-=increment          
            else:
                print("WARN:{}:model.button():paramDict[button] '{}' not implmented".format(self.role,paramDict["button"]))                
                increment=0 #just to strigger the beep
            if increment==0:                
                #music.pitch(frequency=500,duration=150,wait=False) # no beep, pls!!
                pass
            #if increment!=0 #send even if nathing changed, just to recover lost sync with Z
            display.show(self.counter[self.role])
            encoded=pktOut.encode(self.counter[self.role])
            radio.send(encoded)     
        else:
            print("DEBUG:{}:model.button():paramDict[button] '{}' not implmented".format(self.role,paramDict["button"]))                


def messageSend(roleDest,message):
    print("DEBUG:{}:messageAttend({},{})".format(currentRole,roleDest,message))
    


def messageAttend(message):
    print("DEBUG:{}:messageAttend({})".format(currentRole,message))
    
class pkt():
    def encode(self,payload):
        result=versionToken+","
        result+="{},".format(messageBus)
        result+="{},".format(currentRole) #from
        result+=str(payload).replace(",","_coma_")
        return result

    def decode(self,OTAtext,validOriginRoles):
        resultValid=False
        resultDesc=""
        resultFrom=""
        resultPayload=""
        parts=OTAtext.split(",")
        try:
            if parts[0]!=versionToken:
                resultDesc="parts[versionToken]={}, expected:{}".format(parts[0],versionToken)
                errorHandler(halt=False,errorCode=9,desc=resultDesc)
                raise ValueError
            if parts[1]!=str(messageBus):
                resultDesc="parts[messageBus]:{}, expected:{}".format(parts[1],str(messageBus))
                #errorHandler(halt=False,errorCode=9,desc=resultDesc) #too chatty
                raise ValueError
            if parts[2] in validOriginRoles:
                resultFrom=parts[2]
            else:
                resultDesc="parts[originRoles]: {} not in '{}'".format(parts[2],str(validOriginRoles))
                if parts[2] == currentRole:
                    errorHandler(halt=True,errorCode=1,desc="Role cloning: {}".format(currentRole))                
                raise ValueError
            resultPayload=parts[3].replace("_coma_",",")
            resultValid=True
            resultDesc="OK"
        except Exception as e:
            print("DEBUG:pkt.decode:e;{},desc:{},OTAtext:'{}'".format(e,resultDesc,OTAtext))
        return resultValid,resultDesc,resultFrom,resultPayload




def recibido_fila_columna_off():
    display.set_pixel(4,0,0)

def recibido_fila_columna_on():
    display.set_pixel(4,0,9)

def button_a_was_pressed(configAdj):#,model):
    global model
    if configAdj:
        # config change: role in roleList
        global currentRole
        prevRole=currentRole
        roleIndex=roleList.index(currentRole)
        if roleIndex < len(roleList)-1:
            currentRole=roleList[roleIndex+1]
        else:
            currentRole=roleList[0]
        
        model=modelCls(currentRole,model.pktIn,model.pktOut)
        pin_logo_is_touched()
        print("INFO:button_a_was_pressed({}),newRole:{},prevRole,{}".format(configAdj,model.role,prevRole))
    else:
        #display.show("a")
        #encoded=pktOut.encode("a")
        #radio.send(encoded)        
        #recibido_fila_columna_off()
        model.eventHandler(event="button",paramDict={"button":"a"})
        #print("INFO:button_a_was_pressed({}),Role:{}".format(configAdj,currentRole))
    
def button_b_was_pressed(configAdj):#,model):
    if configAdj:
        # config change: messageBus in messageBusesList
        global messageBus
        messageBus+=1
        if messageBus > messageBusMax:
            messageBus=0
        pin_logo_is_touched()
        print("INFO:button_b_was_pressed({}),newbus:{}".format(configAdj,messageBus))
    else:
        #display.show("b")
        #encoded=pktOut.encode("b")
        #radio.send(encoded)        
        #recibido_fila_columna_off()
        model.eventHandler(event="button",paramDict={"button":"b"})
        #print("INFO:button_a_was_pressed({}),Role:{}".format(configAdj,currentRole))


def on_message(message):
    validOriginRoles=validOriginRolesPerDestination[currentRole]
    decoValid,decoDesc,fromRole,decoded=pktIn.decode(message,validOriginRoles)
    print("DEBUG:on_message(pktIn.decode({})):{},'{}','{}'".format(message,decoValid,decoDesc,decoded))
    if decoValid:
        print("INFO:on_message():in from '{}': '{}'".format(fromRole,decoded))
        #display.show(decoded)
        #recibido_fila_columna_on()
        model.message(paramDict={"origin":fromRole,"payload":decoded})
    else:
        print("DEBUG:on_message():pass".format(message,decoValid))         


def pin_logo_is_touched():
    keep_going=True #show Role and messageBus at least once
    while keep_going:
        display.show(currentRole)
        sleep(500)
        display.show(messageBus)
        sleep(200)
        keep_going=pin_logo.is_touched()
        if keep_going:
            print("DEBUG:pin_logo_is_touched(),Role:{},messageBus:{}".format(currentRole,messageBus))
    display.clear()
        
    


if __name__=="__main__":
    display.scroll(versionToken)
    pktIn=pkt()
    pktOut=pkt()
    radio.on()
    radio.config(group=153)#,power=6)
    model=modelCls(currentRole,pktIn,pktOut)
    pin_logo_is_touched()
    model.updateOutput()
    while True:
        if button_a.was_pressed():
            configAdj=pin1.is_touched() # pin1 asserted, config adjustment is in order
            button_a_was_pressed(configAdj)#,model)
        if button_b.was_pressed():
            configAdj=pin1.is_touched() # pin1 asserted, config adjustment is in order
            button_b_was_pressed(configAdj)#,model)
        if pin_logo.is_touched():
            pin_logo_is_touched()
        message = radio.receive()
        if message:
            on_message(message)

# Imports go at the top
from microbit import *
import radio
versionToken="pct2410"
messageBusMax=9 #min is 0, if greater that 9, will scroll y screen, try to avoid it
roleDesc={"A":"perceptron input, weight:1",
     "B":"perceptron input, weight:2",
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

def button_a_was_pressed(configAdj):
    if configAdj:
        # config change: role in roleList
        global currentRole
        prevRole=currentRole
        roleIndex=roleList.index(currentRole)
        if roleIndex < len(roleList)-1:
            currentRole=roleList[roleIndex+1]
        else:
            currentRole=roleList[0]
        pin_logo_is_touched()
        print("INFO:button_a_was_pressed({}),newRole:{},prevRole,{}".format(configAdj,currentRole,prevRole))
    else:
        display.show("a")
        encoded=pktOut.encode("a")
        radio.send(encoded)        
        recibido_fila_columna_off()
        print("INFO:button_a_was_pressed({}),Role:{}".format(configAdj,currentRole))
    
def button_b_was_pressed(configAdj):
    if configAdj:
        # config change: messageBus in messageBusesList
        global messageBus
        messageBus+=1
        if messageBus > messageBusMax:
            messageBus=0
        pin_logo_is_touched()
        print("INFO:button_b_was_pressed({}),newbus:{}".format(configAdj,messageBus))
    else:
        display.show("b")
        encoded=pktOut.encode("b")
        radio.send(encoded)        
        recibido_fila_columna_off()

def on_message(message):
    validOriginRoles=validOriginRolesPerDestination[currentRole]
    decoValid,decoDesc,fromRole,decoded=pktIn.decode(message,validOriginRoles)
    print("DEBUG:on_message(pktIn.decode({})):{},'{}','{}'".format(message,decoValid,decoDesc,decoded))
    if decoValid:
        print("INFO:on_message():in from '{}': '{}'".format(fromRole,decoded))
        display.show(decoded)
        recibido_fila_columna_on()
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
    pktIn=pkt()
    pktOut=pkt()
    radio.on()
    radio.config(group=153)#,power=6)
    while True:
        if button_a.was_pressed():
            configAdj=pin1.is_touched() # pin1 asserted, config change
            button_a_was_pressed(configAdj)
        if button_b.was_pressed():
            configAdj=pin1.is_touched() # pin1 asserted, config change
            button_b_was_pressed(configAdj)
        if pin_logo.is_touched():
            pin_logo_is_touched()
        message = radio.receive()
        if message:
            on_message(message)

import meshtastic.serial_interface
import ignition
import textwrap
import time
import argparse
from pubsub import pub
import yaml
import threading

page = []
emptyline = ""

parser = argparse.ArgumentParser(description="Gateway to Gemini Network")
parser.add_argument("--port", type=str, help="Specify the serial port")

args = parser.parse_args()
interface = meshtastic.serial_interface.SerialInterface(args.port)  # connect to meshtastic

with open("settings.yaml", "r") as file:
    settings = yaml.safe_load(file)
MYNODE = settings.get("MYNODE")        #config who's to listen
USERS = settings.get("USERS")          # List of users

def onReceive(packet, interface):
    #global transmission_count
    #global cooldown
    #global kill_all_robots
    #global weather_info
    #global tides_info
    global DBFILENAME
    #global DM_MODE
    #global FIREWALL
    global emptyline
    Image = 0
    emptyline = ""
    empty = 0
    higher = 0
    iline = ""
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
            message = packet["decoded"]["text"]
            sender_id = packet["from"]
                  
            # Function to handle incoming message, fetch , format and send the gemini website by Meshtastic.
            #print (message)
            if (
            "#get" in message
            and str(packet["to"]) == MYNODE
            and any(node in str(packet["from"]) for node in USERS)
            ): 
                try:  
                    message_parts = message.split(" ")
                    reloadline = ""
                    #print (len(message_parts))
                    if len(message_parts) > 1:
                        url = message_parts[1]
                        
                        if len(message_parts) > 2:
                            reloadline = message_parts[2].rstrip(",")
                    else :
                        url = "gemini://skyjake.fi/gemlog/2023-06_bbs-comments-on-cosmos.gmi"
                    response = ignition.request(url)

                    if response.is_a(ignition.SuccessResponse):
                        print("Success!")
                        
                        text = (response.data())
                        msglength = 175
                        content = ""
                        #tosend = re.findall('.{1,position}',text)
                        
                        lines = text.split("\n")

                        for line in lines: ## split de long msg
                            print ("bob "+line)
                            if len(line) > msglength :
                                w = textwrap.TextWrapper(width=msglength-2, break_long_words=False)
                                line = '\n'.join(w.wrap(line))
                                line = line.rstrip("\n")
                                print (len(line))
                                print ("je separe")
                            content += line + "\n"
                            
                        
                        tosend = content.split("\n")
                        print("-------------------bob")
                        print (len(content))
                        
                        
                        #calculate empty line in text
                        for iindex, eline in enumerate(tosend):
                            
                            if eline == " " or eline == "\r" or eline == "":
                                if  emptyline == "" :
                                    emptyline = str(iindex)
                                    
                                elif iindex <100 :
                                
                                    emptyline = emptyline +","+ str(iindex)
                                empty = empty +1
                        print ("----------------------------")
                        print (len(tosend)-empty)
                        print (emptyline)
                        
                        #print (len(tosend))
                        #if len(tosend) >100 :
                        #    interface.sendText(
                        #                    "C99lines"+str(len(tosend)), wantAck=True, destinationId=sender_id,
                        #                    )
                        #    return
                            
                        #print ()
                        
                        
                        if reloadline != "" :
                            print ("reload")
                            print (reloadline)
                            rline= reloadline.split(",")
                            for rl in rline :
                                
                                if int(rl) < 10 :
                                    send = "0"+rl+tosend[int(rl)]
                                else :
                                    send = rl+tosend[int(rl)]
                                print (send)
                                interface.sendText(send, wantAck=True, destinationId=sender_id,) 
                                time.sleep(1)        
                            
                            return
                        
                        # envoie premiere ligne d'infos
                        addzero = len(tosend) // 10 
                        if addzero >= 0 and addzero < 1 :
                            iline = "00"+str(len(tosend))
                        elif addzero >= 1 and addzero < 10 :
                            iline = "0"+str(len(tosend))
                        else :
                            iline = str(len(tosend))
                        if len(tosend) >100 :
                            iline = "099"
                        interface.sendText(
                            "-\/-"+iline+"-"+emptyline, wantAck=True, destinationId=sender_id,
                            ) 
                        print ("-\/-"+iline+"-"+emptyline)
                        time.sleep(3)
                        
                        
                        for index, line in enumerate(tosend):
                            #print (len(tosend))
                            if index % 5 == 0 :
                                    time.sleep(1)
                                    print("*** Waiting 1 Sec ***")
                                                                                               
                            if index < 10 :
                                iline = "0"+str(index)
                            else :
                                iline = str(index)
                            page.insert(index,line)
                            
                            if line != "" and line !="\r" and line !=" " and index < 99 :
                                interface.sendText(
                                    iline+" "+line, wantAck=True, destinationId=sender_id,
                                    ) 
                                print (iline+" "+line)
                                    #time.sleep(1)
                        #time.sleep(0.5)      
                          
                        emptyline =""
                        
                    elif response.is_a(ignition.InputResponse):
                        interface.sendText(
                            '10 input %s \r\n' % (response.data()), wantAck=True, destinationId=sender_id,
                            ) 
                        print(f"Needs additional input: {response.data()}")

                    elif response.is_a(ignition.RedirectResponse):
                        interface.sendText(
                                'redirect to: %s' % (response.data()), wantAck=True, destinationId=sender_id,
                                ) 
                        print(f"Received response, redirect to: {response.data()}")

                    elif response.is_a(ignition.TempFailureResponse):
                        interface.sendText(
                            'Error from server: %s' % (response.data()), wantAck=False, destinationId=sender_id,
                            ) 
                        print(f"Error from server: {response.data()}")

                    elif response.is_a(ignition.PermFailureResponse):
                        interface.sendText(
                            'Error from server: %s' % (response.data()), wantAck=False, destinationId=sender_id,
                            ) 
                        print(f"Error from server: {response.data()}")

                    elif response.is_a(ignition.ClientCertRequiredResponse):
                        interface.sendText(
                            'Client certificate required. %s' % (response.data()), wantAck=False, destinationId=sender_id,
                            ) 
                        print(f"Client certificate required. {response.data()}")

                    elif response.is_a(ignition.ErrorResponse):
                        interface.sendText(
                            '%s' % (response.data()), wantAck=False, destinationId=sender_id,
                            ) 
                        print(f"There was an error on the request: {response.data()}")
                
                except KeyError as e:
                        interface.sendText(
                            'Error processing packet: %s' % e, wantAck=False, destinationId=sender_id,
                            ) 
                        print(f"Error processing packet: {e}")
    
            
    except KeyError as e:
        print(f"Error processing packet: {e}")




def send_message(message):
    interface.sendText(message)

pub.subscribe(onReceive, 'meshtastic.receive')


while True:
    text = input("> ")
    
    send_message(text)
    

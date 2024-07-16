#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import mimetypes
import os
import shlex
import subprocess
import socket
import socketserver
import ssl
import sys
import tempfile
import urllib.parse
import meshtastic.serial_interface
from pubsub import pub
import os
import time
import json




os.system('cls||clear')
#parser = argparse.ArgumentParser(description="Gateway to Gemini Network")
#parser.add_argument("--port", type=str, help="Specify the serial port")

#args = parser.parse_args()

page = []
capsule = 0
capsule2 = 0
total = 0
lines = 5
url = ""
murl = ""
t0 = time.time()
t1 = time.time()
jumpline = []
resend = 0
inputrequired = 0
redirect = 0
retour = ""
size = 0
try:
    import chardet
    _HAS_CHARDET = True
except ImportError:
    _HAS_CHARDET = False

HOST, PORT = "0.0.0.0", 1965


class AgenaHandler(socketserver.BaseRequestHandler):
    
    def setup(self):
        
        """
        Wrap socket in SSL session.
        """
        self.request = context.wrap_socket(self.request, server_side=True)
        
    def handle(self):
        global url, murl
        # Parse request URL, make sure it's for a Gopher resource  *************************
        self.parse_request()
        #if self.request_scheme != "gopher":
        #    self.send_gemini_header(50, "Agena only proxies to gopher resources.")
        #    return
        # Try to do a Gopher transaction with the remote host  ************************************
        #print (self.download_gopher_resource())
        #print ("parse1-------")
        #print (self.request_path)
        if self.request_query != "":
            urlquery = "?"+self.request_query
            filequery = "!!"+self.request_query
        else :
            urlquery = ""
            filequery = ""
        
        if self.request_path[-1] == "/" and self.request_query == "" :
            filename = "cache/"+self.request_netloc+self.request_path+filequery+"index.gmi"
            url=self.request_netloc+self.request_path+urlquery
            
        else :
            filename = "cache/"+self.request_netloc+self.request_path+filequery
            url=self.request_netloc+self.request_path+urlquery
        #if url != murl :
        #    murl = url
        print (filename)
        #if filename.find == "cotteux" :
        #os.remove(filename) #temporaire desactive le cache
        #url=self.request_netloc+self.request_path+"index.gmi"
        
               
        # Handle what we received based on item type
  
        self.handle_text(filename)
        # Clean up
        self.request.close()
        #os.unlink(filename)

    def send_gemini_header(self, status, meta):
        global lines
        """
        Send a Gemini header, and close the connection if the status code does
        not indicate success.
        """
        #print ("\a")
       
            
        
        if status == 21 :
            self.request.send("{} {}\r\n".format(20, meta).encode("UTF-8"))
            self.request.send("The Page is loading, Be patient !!!\r\n=> gemini://{} At BEEP Click here\r\n".format(url).encode("UTF-8"))
            self.request.send("Page size {} lines \r\n".format(lines).encode("UTF-8"))
            self.request.send("at speed of 15 to 40 bytes/sec on Longfast Channel\r\n".format(url).encode("UTF-8"))
        elif status == 22 :
            self.request.send("{} {}\r\n".format(20, meta).encode("UTF-8"))
            self.request.send("The Page is Too Big, more than 100 lines\r\n".format(url).encode("UTF-8"))
        elif status == 23 :
            self.request.send("{} {}\r\n".format(20, meta).encode("UTF-8"))
            self.request.send("The Page is loading, Be patient !!!\r\n=> gemini://{} At BEEP Click here\r\n".format(url).encode("UTF-8"))
            self.request.send("Page size {} lines \r\n".format(lines).encode("UTF-8"))
            self.request.send("at speed of 15 to 40 bytes/sec on Longfast Channel++\r\n".format(url).encode("UTF-8"))    
        else : 
            self.request.send("{} {}\r\n".format(status, meta).encode("UTF-8"))    
            
        if status / 10 != 2:
            self.request.close()
        
    def parse_request(self):
        """
        Read a URL from the Gemini client and parse it up into parts,
        including separating out the Gopher item type.
        """
        requested_url = self.request.recv(1024).decode("UTF-8").strip()
        if "://" not in requested_url:
            requested_url = "gemini://" + requested_url
        parsed =  urllib.parse.urlparse(requested_url)
             
        self.request_scheme = parsed.scheme
        self.request_netloc = parsed.netloc
        self.request_path = parsed.path
        self.request_query = parsed.query
        #print ("----> "+ requested_url)
        #print (parsed)
        
    
    def handle_text(self, filename):
        """
        Send a Gemini response for a downloaded Gopher resource whose item
        type indicates it should be plain text.
        """
        
        self._serve_file("text/gemini", filename)

        
    def handle_html(self, filename):
        """
        Send a Gemini response for a downloaded Gopher resource whose item
        type indicates it should be HTML.
        """
        self._serve_file("text/html", filename)
        
    

    def _serve_file(self, mime, filename):
        global url,murl,retour,resend
        load = 0
        
        """
        Send a Gemini response with a given MIME type whose body is the
        contents of the specified file.
        """
        
        if filename.find("?")!=0 and filename.find(".cgi")!=0 : # 0 need to be -1
            
            try:
                with open(filename,"rb") as fp:
                    self.send_gemini_header(20, mime)
                    self.request.send(fp.read())
                    fp.close()
                    retour = ""
                
            except IOError:
                print('This file doesn\'t exist. Load from Gemini')
                if murl == url :
                    reload = ""               
                    resend = 1
                    for iline, line in enumerate(page):
                        if len(line) == 0  :
                            reload =  str(iline)+","+reload
                            
                            
               
                    text = "#get "+url+" "+str(reload).rstrip(",")
                    print ("-- "+text)
                    send_message(text)
                    reload = ""
                    self.send_gemini_header(23,"text/gemini")
                else:
                    murl = url
                    send_message("#get "+url)
                    
                    while retour == "" :
                        pub.subscribe(onCheck, 'meshtastic.receive')
                    
                    self.send_gemini_header(int(retour[:2]),retour[3:])
                        
                    retour = ""
        
            
def onReceive(packet, interface):
    global total 
    global capsule
    global page
    global lines
    global t0
    global t1
    global jumpline
    global url , murl
    global resend
    global size
    global redirect
    
    emptyline = ""
    try:
        if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
           
            message_bytes = packet['decoded']['payload']
            print (message_bytes)
                          
            message_string = message_bytes.decode('ISO-8859-1') # to change to utf-8
            
            if message_string[:4] == "-\/-" :
                
                capsule =1
                jumpline.clear()
                total = 0
                resend = 0
                reload = 0
                page.clear()
                t0 = time.time()
                lines = int(message_string[4:7])
                ## receive empty line
                emptyline = message_string[8:]
                
                jumpline = emptyline.split(",")
                total = total + len(jumpline)
                                
                ## create table of the page
                page = [""] * lines
                ###   add empty line to the page
                for space in jumpline :
                    page[int(space)]=" "
               
                emptyline = ""
                #send_message('#okgo')
                            
            tindex = message_string[:2]
            
            #time.sleep(2)
            if tindex.isnumeric() and capsule == 1:
                index = int(tindex)
                
            else :
                print (message_string)
                return
            
            message_final = message_string[2:]
                
            if index > len(page) :
                
                return
            #print ("index "+str(index)+"\r\n")    
            if page[index] == "" :
                page[index]=message_final
                total = total + 1
            os.system('cls||clear')
            print (" Loading .. "+str(total)+"/"+str(lines)+" ::  "+url)
            
            """
            for iline, line in enumerate(page):
                if len(line) != 0 :
                    if iline <=9 :
                        print ("0"+str(iline)+line)
                    else :
                        print (str(iline)+line)
                else :
                        print (str(iline)+" -----Line not received")
            """            
                   
            
            file =""
            
            if (total-len(jumpline) >= 19 and resend == 0 ) or (total-len(jumpline) >= 39 and resend == 1 ): ##or total >=lines*90/100 :
                reload = ""               
                resend = resend +1
                for iline, line in enumerate(page):
                    if len(line) == 0 :
                        reload =  str(iline)+","+reload
                        
                        
                if reload != "" :
                    text = "#get gemini://"+url+" "+str(reload).rstrip(",")
                    print ("-- "+text)
                    send_message(text)
                
                
                                    
            if  total == lines : # check if end of file
                endchar = ""
                os.system('cls||clear')
                filename = url
                endchar = filename[-1]
                directory = filename.split("/")
                
                #print (directory)
                path =""
                if endchar == "/" :
                        file = "index.gmi"
                        
                        
                else :
                        
                        file = directory[len(directory)-1]
                
                for dir in directory:
                    
                    if file != dir :
                        path = path + "/"+dir
                   
                    if not os.path.isdir("./cache/"+path):
                        os.makedirs("./cache"+path) 
                                              
                #print("./cache"+path+file)
                file = file.replace("?","!!")
                f = open("./cache"+path+"/"+file, "w", encoding="utf-8")
                #f.writelines(page)
                #f.close()
                print('\a')
                print('\007')
                print ("url: "+url)
                size = 0
                for iline, line in enumerate(page):
                    size = size + len(line)
                    if iline != total-1 :
                        
                        if line[:1] == " " :
                            f.write(line[1:]+"\n")
                            #print (" "+line[1:])
                        else :
                            f.write(line+"\n")
                            #print (" "+line)
                f.close()  
                t1 = time.time()
                t0t1 = t1-t0
                size = size + len(jumpline)
                print('\a')
                print('\007')
                print (" "+str(len(page))+" lignes en %f secondes"% t0t1)
                print ("  Send "+str(size)+" bytes at "+str(size//t0t1)+" bytes/second")
                
                page.clear()
                jumpline.clear()
                total = 0
                lines = 0
                capsule = 0
                resend = 0
                
                
            
    except KeyError as e:
        print(f"Error processing packet: {e}")
            
def send_message(message):
    #global page
    #page.clear()
    #total = 0
    #line = 0
    #messagetxt = message.replace("%20"," ")
    print (message)
    interface.sendText(message,wantAck=True,destinationId=1976459704) # 1976459704 appg  240558232 tbeam
    
def onCheck(packet, interface):
            
            global retour,url
            retour = ""
            try:
                #print ("je check")
                
                if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
                        
                    message_bytes = packet['decoded']['payload']
                    message_string = message_bytes.decode('ISO-8859-1')
                    #print ("--"+message_string)
                    #print ("--"+message_string[1:34]+"-")
                    if message_string[:8] =="10 input"   :
                        #self.send_gemini_header(10, "Entré necessaire")
                        print ("input required whouwhou")
                        retour = "10 "+message_string[9:]
                       
                    elif message_string[:12] =="redirect to:"   :
                        url = message_string[13:]
                        #self.send_gemini_header(20, url)
                        print ("redirect-------- "+url)
                      
                        retour = "30 "+url
                    elif message_string[:28] =="Client certificate required."   :
                        url = message_string[13:]
                        #self.send_gemini_header(20, url)
                        print ("certificate needed")
                      
                        retour = "60 "+"cert"
                    elif message_string[:9] =="Not Found" or message_string[:12] =="Unknown host" or message_string[:18] =="Connection refused" or message_string[:14] =="Socket timeout" or message_string[:17] =="Error from server":
                        url = message_string[13:]
                        #self.send_gemini_header(20, url)
                        print ("server not found")
                        retour = "50 "+"NO SERVER"
                    elif message_string[:8] =="C99lines"  :
                        url = message_string[9:]
                        #self.send_gemini_header(20, url)
                        print ("server not found-------- "+url)
                      
                        retour = "22 text/gemini"
                    elif message_string[:4]=="-\/-" :
                                
                        retour = "21 text/gemini"
                    else :
                        retour = ""
               
            except KeyError as e:
                print(f"Error processing packet: {e}")

             

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=
"""Agena is a simple Gemini-to-Gopher designed to be run locally to
let you seamlessly access Gopherspace from inside a Gemini client.""")
    parser.add_argument('--cert', type=str, nargs="?", default="cert.pem",
                        help='TLS certificate file.')
    parser.add_argument('--key', type=str, nargs="?", default="key.pem",
                        help='TLS private key file.')
    parser.add_argument('--port', type=str, nargs="?", default=PORT,
                        help='TCP port to serve on.')
    parser.add_argument('--host', type=str, nargs="?", default=HOST,
                        help='TCP host to serve on.')
    args = parser.parse_args()
    print(args)
    interface = meshtastic.serial_interface.SerialInterface(args.port)  # connect to meshtastic
    
    if not (os.path.exists(args.cert) and os.path.exists(args.key)):
        print("Couldn't find cert.pem and/or key.pem. :(")
        sys.exit(1)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=args.cert, keyfile=args.key)

    socketserver.TCPServer.allow_reuse_address = True
    agena = socketserver.TCPServer((args.host, 1965), AgenaHandler)
    pub.subscribe(onReceive, 'meshtastic.receive')
   
    
    try:
        agena.serve_forever()
        
    except KeyboardInterrupt:
        agena.shutdown()
        agena.server_close()


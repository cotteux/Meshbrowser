# Meshbrowser
Prototype to navigate Gemini on meshtastic network

Client and server prototype to navigate trought gemini network.
Very limited.

## Server
setting.yaml to give acces to specifics node.
copy cert.pem and key.pem with the server

## Client
Modify the line 384 in meshbrowser :   interface.sendText(message,wantAck=True,destinationId=1976459704) change the destination id for your server id.

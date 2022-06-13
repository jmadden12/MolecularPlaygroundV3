import socket
import json

HOST = '127.0.0.1'
PORT = 31416

def give_connection():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    print(addr) 
    return conn

def send_move(conn, style, arguments):
    body = {}
    body["type"] = "move"
    body["style"] = style
    if style == "zoom":
        body["scale"] = arguments[0]
    if style == "translate":
        body["x"] = arguments[0]
        body["y"] = arguments[1]
    if style == "rotate":
        return send_sync(conn, "rotateXYBy " + str(arguments[0]) + " " + str(arguments[1]))
    #print(json.dumps(body))
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))
def send_sync(conn, msg):
    body = {}
    body["type"] = "sync"
    body["sync"] = msg
    #print(json.dumps(body))
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))


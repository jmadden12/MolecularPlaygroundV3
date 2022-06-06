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
def send_message(conn, type, style, arguments):
    body = {}
    body["type"] = type
    body["style"] = style
    if style == "zoom":
        body["scale"] = arguments[0]
    if style == "translate":
        body["x"] = arguments[0]
        body["y"] = arguments[1]
    print(json.dumps(body))
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))


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
        return send_command(conn, "zoom " +  str(arguments[0]))
    if style == "translate":
        return send_command(conn, "translate x " + str(arguments[0]) + "; translate y " + str(arguments[1]))
    if style == "rotate":
        return send_command(conn, "rotate y " + str(arguments[0]) + "; rotate x " + str(arguments[1]))
    #print(json.dumps(body))
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))
def send_move_2(conn, style, arguments):
    body = {}
    body["type"] = "move"
    body["style"] = style
    if style == "zoom":
        body["scale"] = arguments[0]
    if style == "translate":
        body["x"] = arguments[0]
        body["y"] = arguments[1]
    if style == "rotate":
        body["x"] = arguments[0]
        body["y"] = arguments[1]
    #print(json.dumps(body))
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))

def send_set_variable(conn, var, data):
    body = {}
    body["var"] = var
    body["data"] = data
    body["type"] = "command"
    body["command"] = ""
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))
def send_content(conn, id):
    body = {}
    body["type"] = "content"
    body["id"] = id
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))
def send_sync(conn, msg):
    body = {}
    body["type"] = "sync"
    body["sync"] = msg
    #print(json.dumps(body))
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))
def send_command(conn, msg):
    body = {}
    body["type"] = "command"
    body["command"] = msg
    conn.sendall(bytes(json.dumps(body) + '\n', 'utf-8'))

    


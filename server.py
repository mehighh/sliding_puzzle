#!/usr/bin/env python3
import socket
import select
import sys
import time
import pickle





HEADER_LENGTH  = 10
PORT           = 5555

# get IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(f"IP: {s.getsockname()[0]}")
IP = s.getsockname()[0]
s.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# reuse address
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()




# indicates if a game is in progress
game_on = False

# list of all sockets
sockets_list = [server_socket]

# storing client data
clients = {}


def receive_message(client_socket):
  try:
    message_header = client_socket.recv(HEADER_LENGTH)

    # if there is no message
    if not len(message_header):
      return False

    message_length = int(message_header.decode("utf-8").strip())
    return {"header": message_header, "data": client_socket.recv(message_length)}

  except:
    return False


while True:
  read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

  for notified_socket in read_sockets:
    if notified_socket == server_socket:
      client_socket, client_address = server_socket.accept()

      user = receive_message(client_socket)

      if user is False:
        continue

      # save new client
      sockets_list.append(client_socket)
      clients[client_socket] = user
      clients[client_socket]['ready'] = False
      print(f"Accepted new connection from {client_address[0]}:{client_address[1]}, username:{user['data'].decode('utf-8')}")

    else:
      message = receive_message(notified_socket)

      if message is False:
        print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")

        # remove socket if there is no message
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
        continue

      if message['data'].decode('utf-8').lower() == 'y':
        clients[notified_socket]['ready'] = True
        user = clients[notified_socket]
        print(f"{user['data'].decode('utf-8')} is ready")

      # forward message to all other clients
      # for client_socket in clients:
      #   if client_socket != notified_socket:
      #     print(f"Forwarding message from {user['data'].decode('utf-8')} to {clients[client_socket]['data'].decode('utf-8')}")
      #     client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

  # remove socket if exception
  for notified_socket in exception_sockets:
    sockets_list.remove(notified_socket)
    del clients[notified_socket]

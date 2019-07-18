#!/usr/bin/env python3
import socket
import select
import copy
import time
import pickle

from game import Game




HEADER_LENGTH  = 15
PORT           = 5555

try:
  # get IP
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect(("8.8.8.8", 80))
  IP = s.getsockname()[0]
  s.close()
except:
  print("No network -> local only")
  IP = "127.0.0.1"

print(f"IP: {IP}")

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


# header format:
# message_size(int) + " " + option
#
# options:
#
#  CLIENT
#  - "init": initial message from client username
#  - "user": send username -> followed by second message
#  - "ready": if client in ready
#  - "result": client game results
#
#  SERVER
#  - "board": server sending the shuffled board to the players
#  - "readyinf": other players being ready
#  - "stat": game statistics



def send_message(option, client_socket = "", message = "no message"):
  if not len(message):
    print("Message is empty -> not sending")
    return False

  if option not in ["board", "readyinf", "stat"]:
    print("Wrong header option")
    return False

  if option == "readyinf":
    # sort names into a list based on if the client is ready or not
    readylist = [[],[]]
    for client in clients:
      if clients[client]['ready'] == False:
        readylist[0].append(clients[client]['data'].decode('utf-8'))
      elif clients[client]['ready'] == True:
        readylist[1].append(clients[client]['data'].decode('utf-8'))

    # turn the list into bytes
    message = pickle.dumps(readylist)

    msgstr = f"{len(message)} {option}"
    message_header = f"{msgstr:<{HEADER_LENGTH}}".encode('utf-8')

    # send the list to every player
    for client in clients:
      client.send(message_header + message)

  elif option == "board":
    GAME = Game()
    GAME.shuffle()
    new_board = GAME.board[:]
    print("Board: ")
    for row in new_board:
      print(row)

    # turn the board into bytes
    message = pickle.dumps(new_board)

    msgstr = f"{len(message)} {option}"
    message_header = f"{msgstr:<{HEADER_LENGTH}}".encode('utf-8')

    # send the board to every player
    for client in clients:
      client.send(message_header + message)

    print("\nSent shuffled board")

  elif option == "stat":
    scoreboard = []
    for client in clients:
      score = clients[client]['time'] + clients[client]['steps']
      scoreboard.append([clients[client]['data'].decode('utf-8'), score])

    # turn the scoreboard into bytes
    message = pickle.dumps(scoreboard)

    msgstr = f"{len(message)} {option}"
    message_header = f"{msgstr:<{HEADER_LENGTH}}".encode('utf-8')

    # send the scoreboard to every player
    for client in clients:
      client.send(message_header + message)

    print("\nSent scoreboard")

  else:
    message = message.encode("utf-8")
    msgstr = f"{len(message)} {option}"
    message_header = f"{msgstr:<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)


def receive_message(client_socket):
  try:
    # get message header
    message_header = client_socket.recv(HEADER_LENGTH)

    # if there is no message
    if not len(message_header):
      return False

    # get message length and option
    message_length = int(message_header.decode("utf-8").split()[0])
    option =         str(message_header.decode("utf-8").split()[1])

    # get message
    message = client_socket.recv(message_length)

    if option not in ["init", "ready", "result"]:
      print("Wrong header option")
      return False

    elif option == "init":
      # save new client
      sockets_list.append(client_socket)
      clients[client_socket] = {"header": message_header, "data": message, "ready": False}

      # send info to every player
      send_message('readyinf')

      print("Sent readyinf")

    elif option == "ready":
      if message.decode('utf-8') == 'y':
        clients[client_socket]['ready'] = True
        print(f"{clients[client_socket]['data'].decode('utf-8')} is ready")

        # send info to every player
        send_message('readyinf')

        print("Sent readyinf")

    elif option == "result":
      results = message.decode('utf-8').split()
      print(f"Got results from {clients[client_socket]['data'].decode('utf-8')}:\n\tSteps: {results[0]}\n\tTime: {results[1]}")
      clients[client_socket]['steps'] = int(results[0])
      clients[client_socket]['time'] = int(float(results[1]))
      clients[client_socket]['done'] = True

  except Exception as e:
    print(f"Recieve error: {str(e)}")
    return False


while True:
  read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

  for notified_socket in read_sockets:
    if notified_socket == server_socket:

      client_socket, client_address = server_socket.accept()

      # clients can only connect when a game is not in progress
      if not game_on:
        if receive_message(client_socket) is False:
          continue

        print(f"Accepted new connection from {client_address[0]}:{client_address[1]}, username:{clients[sockets_list[-1]]['data'].decode('utf-8')}")

    else:

      if receive_message(notified_socket) is False:
        print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")

        # remove socket if there is no message
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
        continue

      # forward message to all other clients
      # for client_socket in clients:
      #   if client_socket != notified_socket:
      #     print(f"Forwarding message from {user['data'].decode('utf-8')} to {clients[client_socket]['data'].decode('utf-8')}")
      #     client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

  # remove socket if exception
  for notified_socket in exception_sockets:
    print(f"Exception -> removing {clients[notified_socket]['data'].decode('utf-8')}")
    sockets_list.remove(notified_socket)
    del clients[notified_socket]



  if not game_on:
    allready = True
    if len(clients):
      for client in clients:
        if not clients[client]['ready']:
          allready = False
    else:
      allready = False

    if allready:
      # START GAME
      game_on = True
      print("Game starting")
      print("Playing:")
      for client in clients:
        clients[client]['ready'] = False
        clients[client]['done'] = False
        print(f"  {clients[client]['data'].decode('utf-8')}")

      # send board to clients
      send_message('board')

  else:
    alldone = True
    if len(clients):
      for client in clients:
        if not clients[client]['done']:
          alldone = False
    else:
      alldone = False

    if alldone:
      # EVALUATE STATS
      send_message('stat')
      game_on = False
      for client in clients:
        clients[client]['done'] = False

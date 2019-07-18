#!/usr/bin/env python3
import sys
import socket
import select
import errno
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

client_username = input("Username: ")
# if the username is 'reader', the client can not send messages, but sees all new messages inmediately

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)




# indicates if client is ready
client_ready = False
RUN = True

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

def send_message(option, message):
  if not len(message):
    print("Message is empty -> not sending")
    return False

  if option not in ["init", "ready", "result"]:
    print("Wrong header option")
    return False


  message = message.encode("utf-8")
  msgstr = f"{len(message)} {option}"
  message_header = f"{msgstr:<{HEADER_LENGTH}}".encode('utf-8')
  client_socket.send(message_header + message)


def receive_message():
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

    if option not in ["board", "readyinf", "stat"]:
      print("Wrong header option")
      return False

    elif option == "readyinf":
      info = pickle.loads(message)
      print('\nNot ready:')

      for cli in info[0]:
        print(f"  {cli}")

      print('Ready:')

      for cli in info[1]:
        print(f"  {cli}")

    elif option == "board":
      board = pickle.loads(message)
      GAME = Game()
      GAME.board = board[:]
      GAME.run()
      stats = f"{GAME.steps} {GAME.time}"
      send_message("result", stats)
      print("\nwaiting for others...")

    elif option == "stat":
      stat_board = pickle.loads(message)
      for row in stat_board:
        print(row)
      quit()

  except Exception as e:
    # print(f"Recieve error {str(e)}")
    return False


def quit():
  print("Press Enter to exit")
  exit()


if __name__ == '__main__':
  # send first message -> server saves username, header
  send_message("init", client_username)

  while RUN:
    message = ""

    try:
      # recieve stuff
      receive_message()

    except IOError as e:
      if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
        print('Reading error', str(e))
        exit()
      continue

    except Exception as e:
      print(str(e))
      exit()

    if client_username != 'reader':
      if not client_ready:
        message = input("Are you ready? (y/n) : ").lower()
        if message == 'y':
          client_ready = True
          send_message("ready", message)


# while True:

#   full_msg = b""
#   new_msg = True
#   while True:
#     msg = s.recv(16)

#     if new_msg:
#       msglen = int(msg[:HEADERSIZE].strip())
#       print(f"New message length: {msglen}")
#       new_msg = False

#     full_msg += msg

#     if len(full_msg)-HEADERSIZE == msglen:
#       print("full msg recvd")
#       d = pickle.loads(full_msg[HEADERSIZE:])
#       print(d)

#       new_msg = True
#       full_msg = b""

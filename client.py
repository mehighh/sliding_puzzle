#!/usr/bin/env python3
import socket
import select
import errno
import pickle




HEADER_LENGTH  = 10
PORT           = 5555

# get IP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print(f"IP: {s.getsockname()[0]}")

IP = s.getsockname()[0]

s.close()

client_username = input("Username: ")
# if the username is 'reader', the client can not send messages, but sees all new messages inmediately

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)




# indicates if client is ready
client_ready = False

def send_message(message):
  if not len(message):
    print("Message is empty -> not sending")
    return False

  message = message.encode("utf-8")
  message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
  client_socket.send(message_header + message)


if __name__ == '__main__':
  # send first message -> server saves username, header
  send_message(client_username)

  while True:
    message = ""

    if client_username != 'reader':
      if not client_ready:
        message = input("Are you ready? (y/n) : ").lower()
        if message == 'y': client_ready = True

    # if there is a message to send
    if message:
      send_message(message)

    try:
      while True:
        # recieve stuff

        # get username header
        username_header = client_socket.recv(HEADER_LENGTH)
        if not len(username_header):
          print("Connection closed by server")
          exit()

        # get the length of the username
        username_length = int(username_header.decode("utf-8").strip())
        # get the username
        username = client_socket.recv(username_length).decode("utf-8")

        # get message header
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(username_header):
          print("No message!")
          continue

        # get the length of the message
        message_length = int(message_header.decode("utf-8").strip())
        # get the message
        message = client_socket.recv(message_length).decode("utf-8")

        print(f"{username} : {message}")

    except IOError as e:
      if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
        print('Reading error', str(e))
        exit()
      continue

    except Exception as e:
      print(str(e))
      exit()


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

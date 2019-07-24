#!/usr/bin/env python3
import socket
import select
import errno
import pickle
import pygame
from game import Game


class Client:

  # header format:
  # message_size(int) + " " + option
  #
  # options:
  #
  #  CLIENT
  #  - "init": initial message from client username
  #  - "ready": if client in ready
  #  - "result": client game results
  #
  #  SERVER
  #  - "board": server sending the shuffled board to the players
  #  - "readyinf": other players being ready
  #  - "stat": game statistics

  def __init__(self):

    self.HEADER_LENGTH  = 15
    self.PORT           = 5555

    try:
      # get IP
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8", 80))
      self.IP = s.getsockname()[0]
      s.close()
    except:
      print("No network -> local only")
      self.IP = "127.0.0.1"

    print(f"IP: {self.IP}")
    print("If this does not match the server IP try typing that in (otherwise just hit Enter)")
    dif_ip = input("Type different IP: ")
    if len(dif_ip):
      self.IP = dif_ip

    self.username = input("\nUsername: ")

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((self.IP, self.PORT))
    self.socket.setblocking(False)


    # GUI stuff
    pygame.init()
    pygame.font.init()

    self.SIZE       = (400,400)
    self.GRID_SIZE  = int(self.SIZE[0]/4)
    self.SCREEN     = pygame.display.set_mode(self.SIZE)
    self.FONT_SIZE  = 20
    self.FONT       = pygame.font.SysFont('Monospace', self.FONT_SIZE)


    # send first message -> server saves username, header
    self.send_message("init", self.username)

    # indicates if client is ready
    self.READY  = False
    self.RUN    = True
    self.OVER   = False
    self.INFO   = []

  def send_message(self, option, message):
    if not len(message):
      print("Message is empty -> not sending")
      return False

    if option not in ["init", "ready", "result"]:
      print("Wrong header option")
      return False


    message = message.encode("utf-8")
    msgstr = f"{len(message)} {option}"
    message_header = f"{msgstr:<{self.HEADER_LENGTH}}".encode('utf-8')
    self.socket.send(message_header + message)


  def receive_message(self):
    try:
      # get message header
      message_header = self.socket.recv(self.HEADER_LENGTH)

      # if there is no message
      if not len(message_header):
        return False

      # get message length and option
      message_length = int(message_header.decode("utf-8").split()[0])
      option =         str(message_header.decode("utf-8").split()[1])

      # get message
      message = self.socket.recv(message_length)

      if option not in ["board", "readyinf", "stat"]:
        print("Wrong header option")
        return False

      elif option == "readyinf":
        self.INFO = pickle.loads(message)[:]
        print('\nNot ready:')

        for cli in self.INFO[0]:
          print(f"  {cli}")

        print('Ready:')

        for cli in self.INFO[1]:
          print(f"  {cli}")

      elif option == "board":
        print('Recieveing boeard')

        try:
          board = pickle.loads(message)

          # start the game with the received board
          GAME = Game(self.SCREEN)
          GAME.board = board[:]
          GAME.run()

          # send score to server
          stats = f"{GAME.steps} {GAME.time}"
          self.send_message("result", stats)
          print("\nwaiting for others...")
          self.OVER = True

        except Exception as e:
          print(f"Game error: {str(e)}")

      elif option == "stat":
        # receive and print statistics
        stat_board = pickle.loads(message)
        for row in stat_board:
          print(row)

        quit()

    except Exception as e:
      # print(f"Recieve error {str(e)}")
      return False


  def quit(self):
    print("Exiting")
    exit()


  def draw(self):
    if self.OVER:
      textsurface = self.FONT.render('Waiting for other players...', False, (255,255,255))
      self.SCREEN.blit(textsurface, (0,0))
    else:
      readytext  = self.FONT.render(f'Ready:',     False, (255,255,255))
      nreadytext = self.FONT.render(f'Not ready:', False, (255,255,255))

      self.SCREEN.blit(readytext,  (0                   ,0))
      self.SCREEN.blit(nreadytext, (int(self.SIZE[0]/2) ,0))

      # info about other players being ready or not
      if len(self.INFO):
        for i,nr in enumerate(self.INFO[0]):
          textsurface = self.FONT.render(f'{nr}', False, (255,255,255))
          self.SCREEN.blit(textsurface, (int(self.SIZE[0]/2), (i+1)*self.FONT_SIZE))

        for i,r in enumerate(self.INFO[1]):
          textsurface = self.FONT.render(f'{r}', False, (255,255,255))
          self.SCREEN.blit(textsurface, (0, (i+1)*self.FONT_SIZE))

      # button
      if not self.READY:
        pygame.draw.rect(self.SCREEN, (255,0,0), ((self.SIZE[0]/2)-30, self.SIZE[1]-20, 60, 20), 0)
        textsurface = self.FONT.render(f'Ready', False, (255,255,255))
        self.SCREEN.blit(textsurface, ((self.SIZE[0]/2)-30, self.SIZE[1]-20))


  def run(self):
    while self.RUN:

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and not self.READY:
          # get the position of the mouse
          mouse_pos = pygame.mouse.get_pos()
          if mouse_pos[0] >= (self.SIZE[0]/2)-30 and mouse_pos[0] <= (self.SIZE[0]/2)+30 and mouse_pos[1] >= self.SIZE[1]-20 and mouse_pos[1] <= self.SIZE[1]:
            self.send_message("ready", "y")
            self.READY = True

      message = ""

      try:
        # recieve stuff
        self.receive_message()

      except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
          print('Reading error', str(e))
          exit()
        continue

      except Exception as e:
        print(str(e))
        exit()

      self.SCREEN.fill(0)
      self.draw()
      pygame.display.flip()

if __name__ == '__main__':
  CLI = Client()
  CLI.run()

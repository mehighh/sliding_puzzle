#!/usr/bin/env python3
import random
import time
import copy
import pygame


class Game:
  def __init__(self, screen):

    # pygame surface
    self.screen = screen

    self.grid_size = int(self.screen.get_size()[0] / 4)

    # for writing text
    self.font = pygame.font.SysFont('Monospace', int((self.grid_size / 4) * 3))

    self.board = [
    [ 1, 2, 3, 4],
    [ 5, 6, 7, 8],
    [ 9,10,11,12],
    [13,14,15, 0]]

    # counting the amout of steps to complete the game
    self.steps = 0

    # the length of the game in seconds
    self.time = 0

    self.game_over = False


  def check_if_over(self):
    test_board = [
    [ 1, 2, 3, 4],
    [ 5, 6, 7, 8],
    [ 9,10,11,12],
    [13,14,15, 0]]

    if str(self.board) == str(test_board):
      self.time = time.time() - self.time
      self.game_over = True
      self.out()
      print("Well done!")
      print(f"Steps: {self.steps}")
      print(f"Time: {self.time}")


  def run(self):
    print("The game started!")

    # for timing the game
    self.time = time.time()

    # mouse acions
    swipe = False
    mouse_pos = []

    while not self.game_over:

      movestr = ""

      # event handling
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          pygame.quit()
          exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
          print("Mouse down")
          swipe = True

          # get the position of the mouse
          mouse_pos = list(pygame.mouse.get_pos())
          mouse_pos[0] = int(mouse_pos[0] / self.grid_size)
          mouse_pos[1] = int(mouse_pos[1] / self.grid_size)
          print(mouse_pos)

        elif event.type == pygame.MOUSEBUTTONUP and swipe == True:
          print("Mouse up")

          # get end position of swipe
          mouse_end = list(pygame.mouse.get_pos())
          mouse_end[0] = int(mouse_end[0] / self.grid_size)
          mouse_end[1] = int(mouse_end[1] / self.grid_size)
          print(mouse_end)

          if mouse_pos == mouse_end or (mouse_pos[0] == mouse_end[0] and mouse_pos[1] == mouse_end[1]):
            print("Not a valid swipe")
            continue

          # if x coordinate doesnt change, the swipe in vertical
          elif mouse_pos[0] == mouse_end[0]:
            movestr = f'v{mouse_pos[1]}'

          # if the x coordinate does not change, th swipe in horizontal
          elif mouse_pos[1] == mouse_end[1]:
            movestr = f'h{mouse_pos[0]}'

          print(movestr)

          self.out()

          if len(movestr) != 2 or movestr[0] not in ['v', 'h'] or int(movestr[1]) not in [0,1,2,3]:
            print("Wrong input")
            continue

          try:
            self.move(movestr[0], int(movestr[1]))
            self.steps += 1
            self.check_if_over()
          except Exception as e:
            print(f"Move error: {str(e)}")

      try:
        self.screen.fill(0)
        self.draw()

        pygame.display.flip()
      except Exception as e:
        print(f"Game run error: {str(e)}")


  def draw(self):
    for j in range(4):
      for i in range(4):
        if self.board[i][j] != 0:
          shade = 255 - (int((255/16) * self.board[i][j]))
          pygame.draw.rect(self.screen,(shade,shade,shade),(j*self.grid_size,i*self.grid_size,self.grid_size,self.grid_size),0)

          textsurface = self.font.render(f'{self.board[i][j]}', False, (255,255,255))
          self.screen.blit(textsurface, (j*self.grid_size, i*self.grid_size))

  def shuffle(self):
    test_board = copy.deepcopy(self.board)
    while self.board == test_board:
      for _ in range(2):
        self.move(random.choice(['v', 'h']),
                  random.randint(0,3))
        # self.out()


  def out(self):
    print("wtf")
    print(self.board)
    for row in self.board:
      print(row)


  def move(self, orientation, pos):
    # orientation: v/h
    # pos: r/c

    if orientation == 'v':
      # rotate board for easier managment
      self.board = list(self.rotated(self.board))

      # reverse rows for easier managment
      for row in self.board:
        row.reverse()
        # print(row)

    zeropos = self.index2d(self.board)
    # print(f"Position of 0: {zeropos}")

    # move 0 to requested index
    del self.board[zeropos[0]][zeropos[1]]
    self.board[zeropos[0]].insert(pos, 0)


    if orientation == 'v':
      # rotate back
      self.board = list(self.rotated(self.board))

      for row in self.board:
        row.reverse()
        # print(row)


  def index2d(self, matrix, element = 0):
    # return (x, y) index of element in a 2d list
    # ONLY IF THERE ARE NO DUPLICATES
    return ([matrix.index(row)  for row in matrix if element in row][0],
            [row.index(element) for row in matrix if element in row][0])


  def rotated(self, matrix):
    list_of_tuples = zip(*matrix[::-1])
    return [list(elem) for elem in list_of_tuples]


if __name__ == '__main__':
  pygame.init()
  pygame.font.init()
  SIZE = (400,400)
  S = pygame.display.set_mode(SIZE)
  g = Game(S)
  g.shuffle()
  g.run()

#!/usr/bin/env python3
import random
import time
import copy

class Game:
  def __init__(self):
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
    self.time = time.time()
    while not self.game_over:
      self.out()
      movestr = input("Move: ")
      if len(movestr) != 2 or movestr[0] not in ['v', 'h'] or int(movestr[1]) not in [0,1,2,3]:
        print("Wrong input")
        continue

      self.steps += 1
      self.move(movestr[0], int(movestr[1]))
      self.check_if_over()


  def shuffle(self):
    test_board = copy.deepcopy(self.board)
    while self.board == test_board:
      for _ in range(2):
        self.move(random.choice(['v', 'h']),
                  random.randint(0,3))
        # self.out()


  def out(self):
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
  g = Game()
  g.shuffle()
  g.run()

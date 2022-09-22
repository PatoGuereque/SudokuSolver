from math import floor
import numpy as np


def flatten_address(row, column):
    return row * 9 + column


def unflatten_address(index):
    return [floor(index / 9), index % 9]


adjacent = []
for i in range(9*9):
    row, column = unflatten_address(i)
    bx = floor(column / 3)
    by = floor(row / 3)
    block = by*3 + bx
    offset = floor(block / 3) * 9 + (block % 3)

    rowi = [i for i in range(row*9, (row+1)*9)]
    coli = [i*9 + column for i in range(9)]
    blocki = np.ravel([range(offset*3 + 9*i, (offset+1)*3 + 9*i)
                      for i in range(3)])
    cells = np.unique(np.ravel([rowi, coli, blocki]))
    adjacent.append(set(cells))

adjacent = np.array(adjacent)


class SudokuBoard(object):

    def __init__(self, board_copy=None) -> None:
        if board_copy is None:
            self.board = np.zeros(9*9, int)
            self.possibilities = [
                {i for i in range(1, 10)} for _ in range(9*9)]
            self.possibility_lengths = np.array([9 for _ in range(81)])
            self.unfilled_cells = {i for i in range(81)}
            self.filled_cells = 0
            self.valid = True
        else:
            self.board = np.copy(board_copy.board)
            self.possibilities = [ele.copy()
                                  for ele in board_copy.possibilities]
            self.possibility_lengths = np.copy(board_copy.possibility_lengths)
            self.filled_cells = board_copy.filled_cells
            self.unfilled_cells = board_copy.unfilled_cells.copy()
            self.valid = True

    def get_possibilities(self, index):
        return self.possibilities[index]

    def fill_value(self, index, value):
        self.board[index] = value
        self.filled_cells += 1
        adj = adjacent[index]
        self.possibilities[index].clear()
        self.possibility_lengths[index] = 0
        self.unfilled_cells.remove(index)

        for adji in adj:
            if value in self.possibilities[adji]:
                self.possibilities[adji].remove(value)
                self.possibility_lengths[adji] -= 1
                if self.possibility_lengths[adji] == 0:
                    self.valid = False

    def is_board_filled(self):
        return self.filled_cells == 81

    def is_value_filled(self, index):
        return self.board[index] != 0

    def fill_next_value(self):
        for cell in self.unfilled_cells:
            if self.possibility_lengths[cell] == 1:
                self.fill_value(cell, self.possibilities[cell].pop())
                return True

        return False

    def is_valid_board(self):
        return self.valid
       
    def get_top_possibility(self):
       min_num = 100
       min_i = -1
       for cell in self.unfilled_cells:
           if self.possibility_lengths[cell] < min_num:
               min_num = self.possibility_lengths[cell]
               min_i = cell
       return min_i

    def get_row(self, row):
        return self.board[row*9:(row+1)*9]

    def print_board(self):
        print("   0 1 2 3 4 5 6 7 8")
        print("  +" + "-----+"*3)
        for row in range(9):
            print(("{} |" + "{} {} {}|"*3).format(row, *
                  [x if x != 0 else " " for x in self.get_row(row)]))
            if row % 3 == 2:
                print("  +" + "-----+"*3)

    def initialize_board(self, array):
        for i, val in enumerate(array):
            if val != 0:
                self.fill_value(i, val)


def solve_sudoku(board: SudokuBoard):
    # exit condition
    if board.is_board_filled():
        return board

    # check if board is valid
    if not board.is_valid_board():
        return None

    # fill values with 1 single possibility
    if board.fill_next_value():
        return solve_sudoku(board)

    idx = board.get_top_possibility()
    possibilities = board.get_possibilities(idx)

    for possibility in possibilities:
        boardc = SudokuBoard(board_copy=board)
        boardc.fill_value(idx, possibility)

        sol = solve_sudoku(boardc)
        if sol is not None:
            return sol

    return None

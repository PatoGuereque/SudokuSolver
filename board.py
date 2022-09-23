from math import floor
import numpy as np


def flatten_address(row, column):
    """Transforms a row and column address to an index

    Arguments
    ---------
    row : int
        The row number (0 indexed)
    column : int
        The column number (0 indexed)

    Returns
    -------
    index
    """
    return row * 9 + column


def unflatten_address(index):
    """Transforms an address index into a row and column

    Arguments
    ---------
    index : int
        the cell index

    Returns
    -------
    row, column
    """
    return [floor(index / 9), index % 9]


def generate_adjacent_cache():
    """Generates a cache of all the groups of cells a cell belongs to

    For each cell in the sudoku, cache all the cells the current cell can see.
    All the indices of cells in the current row, column and block. This is
    for a fast lookup cache when needing to remove all possibilities

    Returns:
    An array of 81 elements (one for each cell in the sudoku) with all of
    the group of cells
    """
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
    return np.array(adjacent)


adjacent = generate_adjacent_cache()


class SudokuBoard(object):
    """A class used to represent a Board

    The board is flattened to an array

    The following board with the X on row 1, column 4

       0 1 2 3 4 5 6 7 8
      +-----+-----+-----+
    0 |     |     |     |
    1 |     |  X  |     |
    2 |     |     |     |
      +-----+-----+-----+
    3 |     |     |     |
    4 |     |     |     |
    5 |     |     |     |
      +-----+-----+-----+
    6 |     |     |     |
    7 |     |     |     |
    8 |     |     |     |
      +-----+-----+-----+

    The translation formula is as follow:

        index = (row * 9) + column

    Replacing for the row 1 and column 4 would yield (1 * 9) + 4 = 13. 
    The X would belong to the index 13 of the array.

    Attributes
    ----------
    board : array
        The sudoku board flattened to an array. 0 means that the cell is empty.
        The other possible values are 1 to 9 (inclusive)
    possibilities : list of sets of numbers
        All of the possible numbers each cell can have. Initialized with sets
        with values [1...9], but updated when SudokuBoard#fill_value is called
    unfilled_cells : set of numbers
        The indices of the cells that are not filled
    filled_cells : int
        The number of filled cells (to check whether the board is completed
        or not)
    valid : boolean


    Methods
    -------
    says(sound=None)
        Prints the animals name and what sound it makes
    """

    def __init__(self, board_copy=None) -> None:
        """SudokuBoard constructor

        This initializes an empty board if no board_copy parameter is set.
        If the board_copy parameter is provided, all of the attributes from
        board_copy will get deep copied

        Arguments
        ---------
        (optional) board_copy : SudokuBoard
            A sudokuBoard to copy
        """
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
        """Retrieves all of the possible values for the given cell

        No computation is required as all of the possibilities are cached and
        updated automatically by the fill_value method

        Arguments
        ---------
        index : int
           The cell index

        Returns
        -------
        A set of all of the possible values that cell can have
        """
        return self.possibilities[index]

    def fill_value(self, index, value):
        """Fills a cell in the board

        This sets the specific cell in the board to the value provided and
        removes itself from the possibilities of the cells that share the
        column, row, and block. Additionally checks if the board is in a
        valid state, meaning that the rest of the cells can have values

        Arguments
        ---------
        index : int
            The cell index of the board to set
        value : int [1 to 9]
            The value of the cell to set 
        """
        self.board[index] = value
        self.filled_cells += 1
        adj = adjacent[index]
        self.possibilities[index].clear()
        self.possibility_lengths[index] = 0
        self.unfilled_cells.remove(index)

        for adji in adj:
            # remove itself from the possibilities of adjacent cells
            if value in self.possibilities[adji]:
                self.possibilities[adji].remove(value)
                self.possibility_lengths[adji] -= 1

                # check if board is valid
                if self.possibility_lengths[adji] == 0:
                    self.valid = False

    def is_board_filled(self):
        """Checks if the board is completely filled

        Returns
        -------
        true if the board is filled
        """
        return self.filled_cells == 81

    def is_value_filled(self, index):
        """Checks if the cell is filled

        Arguments
        ---------
        index : int
            The cell index of the board to set

        Returns
        -------
        true if the cell is filled
        """
        return self.board[index] != 0

    def fill_next_value(self):
        """Fills the next available cell with the only possibility

        From all of the unfilled cells, if the cell has only one possibility
        we can safely set it to that, since on that specific path there was
        no other options.

        Returns
        -------
        true if a cell could be successfully filled
        """
        for cell in self.unfilled_cells:
            if self.possibility_lengths[cell] == 1:
                self.fill_value(cell, self.possibilities[cell].pop())
                return True

        return False

    def is_valid_board(self):
        """Checks if the board is valid

        This value is computed automatically from the fill_value method

        Returns
        -------
        true if the board is valid
        """
        return self.valid

    def get_top_possibility(self):
        """Gets the top suitable index to try the possible combinations

        The best suitable index is the one who has the least possibilities,
        to start branching out from there.

        Returns
        -------
        int (the index)
        """
        min_num = 100
        min_i = -1
        for cell in self.unfilled_cells:
            if self.possibility_lengths[cell] < min_num:
                min_num = self.possibility_lengths[cell]
                min_i = cell

        return min_i

    def print_board(self):
        """Prints the board to the console

        An example output is:

           0 1 2 3 4 5 6 7 8
          +-----+-----+-----+
        0 |     |    6|     |
        1 |  5 9|     |    8|
        2 |2    |    8|     |
          +-----+-----+-----+
        3 |  4 5|     |     |
        4 |    3|     |     |
        5 |    6|    3|  5 4|
          +-----+-----+-----+
        6 |     |3 2 5|    6|
        7 |     |     |     |
        8 |     |     |     |
          +-----+-----+-----+
        """
        print("   0 1 2 3 4 5 6 7 8")
        print("  +" + "-----+"*3)
        for row in range(9):
            print(("{} |" + "{} {} {}|"*3).format(row, *
                  [x if x != 0 else " " for x in self.board[row*9:(row+1)*9]]))
            if row % 3 == 2:
                print("  +" + "-----+"*3)

    def initialize_board(self, array):
        """Initializes the board with an array of values

        Arguments
        ---------
        array : iterable of ints
            The array of values to initialize the board with
        """
        for i, val in enumerate(array):
            if val != 0:
                self.fill_value(i, val)


def solve_sudoku(board: SudokuBoard):
    """Solves the provided sudoku

    This is a recursive function that will use a Depth-First search technique
    in order to iterate over the cell possibilities and find a solution. It
    will only return the first successful solution found, or none if board
    is unsolvable. This will happen if the input board is unsolvable.

    Arguments
    ---------
    board : SudokuBoard
        The board to solve

    Returns
    -------
    A solved sudoku board if possible, otherwise None
    """
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

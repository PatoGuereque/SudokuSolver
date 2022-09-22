from board import SudokuBoard, solve_sudoku
import tests.boards as boards

board = SudokuBoard()
board.initialize_board(boards.canvas_board)
board.print_board()
board = solve_sudoku(board)
board.print_board()
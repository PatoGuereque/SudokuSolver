import tests.boards as boards
import timeit
from board import SudokuBoard, solve_sudoku
from statistics import fmean
from rich.console import Console
from rich.table import Table
from rich.progress import Progress


def wrap_benchmark(board):
    def _wrap_benchmark():
        board_copy = SudokuBoard(board_copy=board)
        solve_sudoku(board_copy)
    return _wrap_benchmark


def benchmark(table, name, raw_board):
    board = SudokuBoard()
    board.initialize_board(raw_board)

    results = [
        x*1000 for x in timeit.repeat(wrap_benchmark(board), repeat=200, number=1)]
    table.add_row(
        name,
        "{:.3f}".format(min(results)),
        "{:.3f}".format(max(results)),
        "{:.3f}".format(fmean(results)))


console = Console()

table = Table(show_header=True, header_style="bold magenta")
table.add_column("Sudoku", style="dim")
table.add_column("Min (ms)", justify="right")
table.add_column("Max (ms)", justify="right")
table.add_column("Mean (ms)", justify="right")

benchmarks = [
    ("easy", boards.easy_board),
    ("medium", boards.medium_board),
    ("hard", boards.hard_board),
    ("evil", boards.evil_board),
    ("canvas", boards.canvas_board),
    ("al escargot", boards.al_escargot),
    ("arto inkala", boards.arto_inkala),
    ("unsolvable 515", boards.unsolvable_515),
    ("unsolvable 28", boards.unsolvable_28),
    ("unsolvable 49", boards.unsolvable_49),
]

with Progress(console=console,) as progress:
    task = progress.add_task("Benchmarking....", total=len(benchmarks))

    for name, board in benchmarks:
        progress.update(task_id=task, advance=0, description=f'Benchmarking {name}...')
        benchmark(table, name, board)
        progress.update(task_id=task, advance=1, description=f'Benchmarking {name}...')

console.print(table)

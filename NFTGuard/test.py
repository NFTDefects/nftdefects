
# from rich.progress import track
# import time
# for step in track(range(100)):
#     print('i love china!')
#     print(step)
#     time.sleep(0.02)

# # track(0.222)
# print("1111")

from rich import print
from rich.table import Table

grid = Table.grid(expand=True)
grid.add_column()
grid.add_column(justify="right")
grid.add_row("Raising shields", "[bold magenta]COMPLETED [green]:heavy_check_mark:")

from rich.table import Column
table = Table(
    "Released",
    "Title",
    Column(header="Box Office", justify="right"),
    title="Star Wars Movies"
)
print(table)

print(grid)
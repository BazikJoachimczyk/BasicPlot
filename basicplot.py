import sys, os
from .plot_all import Plot()
from .time_scale import TimeScale12hrs()
from .create_objects import BuildObjectsList()

def run():
    if len(sys.argv != 1):
        print("Usage: <path_to_text_file>".format(sys.argv[0]))

    path = sys.argv[1]

    if os.path.isfile(path) == False:
        print(f"File: {path} not found.")
        return


    objects = BuildObjectsList(path)
    timescale = TimeScale12hrs()
    Plot(objects, timescale)


if __name__ == '__main__':
    run()
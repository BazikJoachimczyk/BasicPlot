import sys, os
import plot_all, time_scale, create_objects

def run():
    if len(sys.argv) != 1:
        print("Usage: <path_to_text_file>".format(sys.argv[0]))

    path = sys.argv[1]

    if os.path.isfile(path) == False:
        print(f"File: {path} not found.")
        return


    objects = create_objects.BuildObjectsList(path)
    timescale = time_scale.TimeScale12hrs()
    plot_all.Plot(objects, timescale)


if __name__ == '__main__':
    run()
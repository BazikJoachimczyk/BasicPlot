import sys, os
import plot_all, time_scale, create_objects

def run():
    if len(sys.argv) != 3:
        print("Usage: {} <mode> <path_to_text_file>".format(sys.argv[0]))
        sys.exit(1)
    
    mode = sys.argv[1]
    path = sys.argv[2]

    if os.path.isfile(path) == False:
        print(f"File: {path} not found.")
        return

    if mode == 'tonight':
        timescale = time_scale.TimeScaleForTheNight()
        print('Calculating visibility for the night...', flush=True)
    elif mode == '12':
        timescale = time_scale.TimeScale12hrs()
        print('Calculating visibility for the next 12 hours...', flush=True)
    else:
        print("Invalid mode. Use 'tonight' or '12'.")
        sys.exit(1)

    objects = create_objects.BuildObjectsList(path)
    plot_all.Plot(objects, timescale)


if __name__ == '__main__':
    run()
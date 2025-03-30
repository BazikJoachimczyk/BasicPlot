import sys, os, threading
import plot_all, time_scale, create_objects
import argparse
import moon_separations

def run():
    if len(sys.argv) != 3:
        print("Usage: {} <mode> <path_to_text_file>".format(sys.argv[0]))
        sys.exit(1)
    
    mode = sys.argv[1]

    if mode == 'tonight' or mode == '12' and os.path.isfile(sys.argv[2]) == True:
        path = sys.argv[2]
    elif mode == 'tonight' or mode == '12' and os.path.isfile(sys.argv[2]) == False:
        print(f"File: {path} not found.")
        return

    if mode == 'tonight':
        path = sys.argv[2]
        timescale = time_scale.TimeScaleForTheNight()
        print('Calculating visibility for the night...', flush=True)

    elif mode == '12':
        path = sys.argv[2]
        timescale = time_scale.TimeScale12hrs()
        print('Calculating visibility for the next 12 hours...', flush=True)

    elif mode == 'ui':
        parser = argparse.ArgumentParser(description="Read astronomical parameters from the terminal.")

        parser.add_argument('-ra', type=str, required=True, help="Right Ascension in hh:mm:ss format.")
        parser.add_argument('-dec', type=str, required=True, help="Declination in +-dd:mm:ss format.")
        parser.add_argument('-lat', type=str, required=True, help="Latitude in +-dd:mm:ss format (+ is north, - is south.)")
        parser.add_argument('-lon', type=str, required=True, help="Longitude in +-dd:mm:ss format (+ is east, - is west).")
        args = parser.parse_args()
        
        
    else:
        print("Invalid mode. Use 'tonight' or '12'.")
        sys.exit(1)

    objects = create_objects.BuildObjectsList(path)
    plot_all.Plot(objects, timescale)
    moon_separations.PlotMoonSeparation(objects, timescale)


if __name__ == '__main__':
    run()
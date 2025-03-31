import sys, os, threading
import plot_all, time_scale, create_objects, calculate_visibility
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

def run2():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument("-mode", choices = ["tonight", "12", "ui"], required=True, help="Mode: 'tonight' for full night, '12' for the next 12 hours, 'ui' for JSON format.")
    parser.add_argument("-file", type=str, help="Path to text file with coordinates.", required=False)

    # UI arguments
    parser.add_argument("-ra", type=str, help="Right Ascension in hh:mm:ss format.")
    parser.add_argument("-dec", type=str, help="Declination in +-dd:mm:ss format.")
    parser.add_argument("-lat", type=str, help="Latitude in +-dd:mm:ss format (+ is north, - is south).")
    parser.add_argument("-lon", type=str, help="Longitude in +-dd:mm:ss format (+ is east, - is west).")

    args = parser.parse_args()
    mode = args.mode
    
    if mode in ["tonight", "12"]:
        if not args.file:
            print("Error: -file argument is required for 'tonight' and '12' modes.")
            sys.exit(1)
        if not os.path.isfile(args.file):
            print(f"Error: File '{args.file}' not found.")
            sys.exit(1)
        path = args.file
        
        if mode == "tonight":
            timescale = time_scale.TimeScaleForTheNight()
            print("Calculating visibility for the night...", flush=True)
        elif mode == "12":
            timescale = time_scale.TimeScale12hrs()
            print("Calculating visibility for the next 12 hours...", flush=True)
    
        #tutaj tradycyjny plot
        objects = create_objects.BuildObjectsList(path)
        plot_all.Plot(objects, timescale)
        moon_separations.PlotMoonSeparation(objects, timescale)

    elif mode == "ui":
        if not all([args.ra, args.dec, args.lat, args.lon]):
            print("Error: -ra, -dec, -lat, and -lon arguments are required for 'ui' mode.")
            sys.exit(1)
        
        print(f"Using manual input: RA={args.ra}, Dec={args.dec}, Lat={args.lat}, Lon={args.lon}")
    
    #tutaj plot dla UI, czyli same wysokości 
        timescale = time_scale.TimeScale12hrs()
        calculate_visibility.UIAltitudes(ra_str=args.ra, dec_str=args.dec, lat_str=args.lat, lon_str=args.lon, time=timescale)


    else:
        print("Invalid mode. Use 'tonight', '12', or 'ui'.")
        sys.exit(1)



if __name__ == "__main__":
    run2()

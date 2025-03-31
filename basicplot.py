import sys, os, threading
import plot_all, time_scale, create_objects, calculate_visibility
import argparse
import moon_separations

def run():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument("-mode", choices = ["tonight", "12", "ui"], required=True, help="Mode: 'tonight' for full night, '12' for the next 12 hours, 'ui' for JSON format.")
    parser.add_argument("-file", type=str, help="Path to text file with coordinates.", required=False)

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
    
        objects = create_objects.BuildObjectsList(path)
        plot_all.Plot(objects, timescale)
        moon_separations.PlotMoonSeparation(objects, timescale)

    elif mode == "ui":
        if not all([args.ra, args.dec, args.lat, args.lon]):
            print("Error: -ra, -dec, -lat, and -lon arguments are required for 'ui' mode.")
            sys.exit(1)
        
        print(f"Using manual input: RA={args.ra}, Dec={args.dec}, Lat={args.lat}, Lon={args.lon}")
    
        timescale = time_scale.TimeScale12hrs()
        calculate_visibility.UIAltitudes(ra_str=args.ra, dec_str=args.dec, lat_str=args.lat, lon_str=args.lon, time=timescale)


    else:
        print("Invalid mode. Use 'tonight', '12', or 'ui'.")
        sys.exit(1)



if __name__ == "__main__":
    run()

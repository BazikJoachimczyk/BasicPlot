"""Visibility plot for the high priority northern targets from the weekly BHTOM newsletter.

Usage:
    python newsletter.py email.txt [-mode tonight|12] [-save targets.txt]

Save the e-mail body as a text file (or pass '-' and paste it into stdin).
"""
import sys, os
import re
import argparse
import plot_all, time_scale
from create_objects import Object

NORTH_HEADER = re.compile(r'^\s*North\s*\(dec\s*>\s*0\)\s*:', re.IGNORECASE)
TABLE_HEADER = re.compile(r'^\s*name\s+ra\s+dec\b', re.IGNORECASE)
# name may contain spaces and integers ("LS I +61 302"), so it ends at the first decimal number
TARGET_ROW = re.compile(
    r'^(?P<name>\S.*?)\s+(?P<ra>\d+\.\d+)\s+(?P<dec>[+-]?\d+\.\d+)'
    r'\s+(?P<mag>[+-]?\d+(?:\.\d+)?)\s+(?P<sun_sep>\d+(?:\.\d+)?)(?:\s+(?P<rest>.*))?$')


def SplitClassification(rest: str):
    # classification can have spaces ("BL Lac"), so it can only be separated when tabs survived
    if '\t' in rest:
        classification, _, description = rest.partition('\t')
        return classification.strip(), description.strip()
    return '', rest.strip()


class Target(Object):
    def __init__(self, name, ra, dec, mag, sun_separation, classification = '', description = ''):
        super().__init__(name, ra, dec)
        self.mag = float(mag)
        self.sun_separation = float(sun_separation)
        self.classification = classification
        self.description = description


def ParseNorthTargets(text: str):
    """Return the targets listed under 'North (dec>0):' in the newsletter."""
    targets = []
    in_section = False
    for line in text.splitlines():
        if not in_section:
            in_section = bool(NORTH_HEADER.match(line))
            continue
        if not line.strip() or TABLE_HEADER.match(line):
            continue
        row = TARGET_ROW.match(line.strip())
        if row is None:                         # 'South (dec<0):' or anything after the table
            break
        classification, description = SplitClassification(row['rest'] or '')
        targets.append(Target(row['name'].strip(), row['ra'], row['dec'], row['mag'], row['sun_sep'],
                              classification, description))
    if not in_section:
        raise ValueError("No 'North (dec>0):' section found - is this a BHTOM newsletter?")
    return targets

def SaveTargets(targets: list, path: str):
    # same format as the -file input of basicplot.py
    with open(path, 'w') as file:
        for t in targets:
            file.write(f"{t.name} {t.ra} {t.dec}\n")


def run(argv=None):
    parser = argparse.ArgumentParser(description="Plot visibility of high priority northern targets from the BHTOM newsletter.")
    parser.add_argument("email", help="Text file with the newsletter e-mail ('-' reads stdin).")
    parser.add_argument("-mode", choices = ["tonight", "12"], default="tonight", help="'tonight' for full night, '12' for the next 12 hours.")
    parser.add_argument("-save", type=str, help="Also save targets as '<name> <ra> <dec>' list usable with basicplot.py -file.")
    args = parser.parse_args(argv)

    if args.email == '-':
        text = sys.stdin.read()
    else:
        if not os.path.isfile(args.email):
            print(f"Error: File '{args.email}' not found.")
            sys.exit(1)
        with open(args.email, 'r', encoding='utf-8') as file:
            text = file.read()

    try:
        targets = ParseNorthTargets(text)
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)
    if not targets:
        print("Error: 'North (dec>0):' section contains no targets.")
        sys.exit(1)

    print(f"Found {len(targets)} northern high priority targets:")
    for i, t in enumerate(targets, start = 1):
        print(f"{i:3d}  {t.name:32s} {t.ra:11.6f} {t.dec:+10.6f}  {t.mag:5.1f} mag  {t.classification}")

    if args.save:
        SaveTargets(targets, args.save)
        print(f"Saved target list to {args.save}")

    timescale = time_scale.TimeScaleForTheNight() if args.mode == "tonight" else time_scale.TimeScale12hrs()
    plot_all.Plot(targets, timescale)


if __name__ == "__main__":
    run()

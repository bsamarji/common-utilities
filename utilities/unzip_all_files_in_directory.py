# use sys module so we can run this script on command line and pass args to the script
import sys
import argparse
import zipfile
from pathlib import Path

# use argparse to create cli (command line interface)
# the cli will allow named args to be passed to the python script
parser = argparse.ArgumentParser()

# add command line arguments to parser
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument("--tdir", help="path of target directory that contains .zip files.",
                           type=str, required=True)
requiredNamed.add_argument("--odir", help="path of output directory to send the unzipped files to.",
                           type=str, required=True)

# check if any arguments were passed to the script via the command line
# if no arguments were passed then print message about help and then exit program
if not len(sys.argv) > 1:
    print("No arguments were passed by the user to the script.\n"
          "Please pass the required arguments to the script via command line.\n"
          "Use the -h or --help argument to bring up the cli documentation.")
    sys.exit(1)
# if arguments were passed then the program continues
else:
    # pass the arguments into a python namespace
    # we can then use the names of the args as variables
    args = parser.parse_args()
    print(f"passed args to {sys.argv[0]}:\ntarget directory: {args.tdir}\noutput directory: {args.odir}")


# define function to extract zip files
def extract_zip_files(directory, output_path):
    # validate that the directory exists
    if Path(directory).is_dir() is True:
        # extract .zip file(s)
        p = Path(directory)
        for f in p.glob('*.zip'):
            with zipfile.ZipFile(f, 'r') as archive:
                archive.extractall(path=output_path)
                print(f"Extracted contents from '{f.name}' to '{output_path}' directory.")
    else:
        print(f"The directory: '{directory}' does not exist.")
        print("Please pass a directory that does exist.")
        sys.exit(1)


try:
    # call function using passed parameters from command line
    extract_zip_files(directory=args.tdir, output_path=args.odir)

except IndexError:
    print("This program requires 2 arguments to be passed.")
    print("The first argument is the directory containing the .zip files.")
    print("The second argument is the directory you wish to output the extracted .zip files to.")
    sys.exit(1)

except zipfile.BadZipFile:
    print("The zip file(s) are corrupted.")
    sys.exit(1)

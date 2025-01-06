import argparse
import paramiko
import sys
import os

# use argparse to create cli (command line interface)
# the cli will allow named args to be passed to the python script
# this will enable the script to be re-used to access multiple different sftp sites
parser = argparse.ArgumentParser()

# add command line arguments to parser
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument("--host", help="sftp hostname", type=str)
requiredNamed.add_argument("--user", help="sftp username", type=str)
requiredNamed.add_argument("--pw", help="sftp password", type=str)
requiredNamed.add_argument("--port", help="sftp port", type=int)
# we provide the host key as a txt file to paramiko
# the argument passed should be the full file path and name to the host key txt file
# if the host key file does not exist, or you do not know it,
# the script will auto add a host key and save it in the file name provided (look at try except statement)
requiredNamed.add_argument("--hkey", help="sftp host key txt file path and name. "
                                          "If the host key file does not exist, or you do not know it, the script will "
                                          "auto add a host key and save it in the file name passed.", type=str)
requiredNamed.add_argument("--rdir", help="remote directory file path and name "
                                          "(this is the remote file you wish to download)", type=str)
requiredNamed.add_argument("--ldir", help="local directory file path and name "
                                          "(this is where you want to download the remote file to)", type=str)

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
    print(f"passed args to {sys.argv[0]}:\nhostname: {args.host}\nusername: {args.user}\npassword: {args.pw}\n"
          f"port: {args.port}\n"f"remote directory: {args.rdir}\nlocal directory: {args.ldir}")

# if the host key file does not exist then auto add the host key and create a new host key file
try:
    with open(args.hkey) as f:
        print("Host key file exists")
except FileNotFoundError:
    print("Host key file does not exist, now creating one.")
    with paramiko.SSHClient() as client:
        # auto add the host key information to client when we try and connect to the sftp site
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=args.host, username=args.user, password=args.pw, port=args.port)
        # save host key information into file
        client.get_host_keys().save(args.hkey)
        print(f"Created host key file: {args.hkey}")

# connect to sftp and download file from remote directory to local directory
with paramiko.SSHClient() as client:
    client.load_host_keys(args.hkey)
    print(f"Loaded host key from file: {args.hkey}")
    client.connect(hostname=args.host, username=args.user, password=args.pw, port=args.port)
    print(f"Connected to SFTP: {args.host}")

    # download remote file to local directory
    with client.open_sftp() as sftp:
        # the parameter max_concurrent_prefetch_requests enable large file downloads (100 MB or more)
        # without it end of file exceptions will occur
        # 64 is the OpenSSH Standard for max_concurrent_prefetch_requests
        sftp.get(remotepath=args.rdir, localpath=args.ldir, max_concurrent_prefetch_requests=64)
        print(f"Got remote file: {args.rdir} and put it in local dir: {args.ldir}")
        # check if the file has been downloaded properly and exists on the local hard drive
        if os.path.isfile(args.ldir):
            print(f"The file: {args.ldir} exists. The download was successful.")
        else:
            print(f"The file: {args.ldir} does not exist. The download was unsuccessful.")

# close connection to sftp
client.close()
print(f"Closed connection to SFTP: {args.host}")

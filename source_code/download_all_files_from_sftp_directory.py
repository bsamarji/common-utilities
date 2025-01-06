import argparse
import paramiko
import sys
import os
import stat

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
requiredNamed.add_argument("--rdir", help="remote directory path", type=str)
requiredNamed.add_argument("--ldir", help="local directory path", type=str)

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

    # download all remote files to local directory
    with client.open_sftp() as sftp:
        # get list of objects in remote dir so we can loop through all the files and download them
        file_list = sftp.listdir(args.rdir)
        for file in file_list:
            # concat remote path and file name together, so it can be used in sftp.get()
            r_file = os.path.join(args.rdir, file)
            # get remote object attributes, so we can check if it is a file or dir
            r_file_attr = sftp.lstat(r_file)
            # concat local path and file name together, so it can be used in sftp.get()
            l_file = os.path.join(args.ldir, file)
            # if the object is a file then download it
            if stat.S_ISREG(r_file_attr.st_mode):
                # the parameter max_concurrent_prefetch_requests enable large file downloads (100 MB or more)
                # without it end of file exceptions will occur
                # 64 is the OpenSSH Standard for max_concurrent_prefetch_requests
                sftp.get(remotepath=r_file, localpath=l_file, max_concurrent_prefetch_requests=64)
                print(f"Got remote file: {r_file} and put it in local dir: {l_file}")
                # check if the file has been downloaded properly and exists on the local hard drive
                if os.path.isfile(l_file):
                    print(f"The file: {l_file} exists. The download was successful.")
                else:
                    print(f"The file: {l_file} does not exist. The download was unsuccessful.")
            # if the object is not a file, then remove it from the list
            else:
                file_list.remove(file)

# close connection to sftp
client.close()
print(f"Closed connection to SFTP: {args.host}")

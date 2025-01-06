import argparse
import ftplib
import sys
import os
import ftputil
# this is required for the session factory variable
import ftputil.session as session

# use argparse to create cli (command line interface)
# the cli will allow named args to be passed to the python script
# this will enable the script to be re-used to access multiple different ftp sites
parser = argparse.ArgumentParser()

# add command line arguments to parser
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument("--host", help="ftp hostname", type=str)
requiredNamed.add_argument("--user", help="ftp username", type=str)
requiredNamed.add_argument("--pw", help="ftp password", type=str)
requiredNamed.add_argument("--rdir", help="remote directory file path and name "
                                          "(this is the remote file you wish to download)", type=str)
requiredNamed.add_argument("--ldir", help="local directory file path and name "
                                          "(this is where you want to download the remote file to)", type=str)
# mode is an optional argument because it has a default value
# that is why it has been added to the parser and not requiredNamed
# parser will show it as optional when -h arg is used
parser.add_argument("--mode", help="set the transfer mode to active or passive. "
                                   "pass either 'active' or 'passive' for this argument."
                                   "The default value for this argument is: active", type=str, default="active")
# the port is set to the default value for ftp: 21. Therefore, it is an optional arg
parser.add_argument("--port", help="ftp port. The default value is set to 21.", type=int, default=21)

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
    # python can then use the names of the args as object attributes
    args = parser.parse_args()
    print(f"passed args to {sys.argv[0]}:\nhostname: {args.host}\n"
          f"username: {args.user}\npassword: {args.pw}\n"
          f"port: {args.port}\n"f"remote directory: {args.rdir}\n"
          f"local directory: {args.ldir}\ntransfer mode: {args.mode}")

# configure a session factory for either active or passive transfer connections (if neither are true then raise error)
# the session factory also lets the user configure the ftp port (by default it is set to 21)
if args.mode == "active":
    my_session_factory = session.session_factory(
        base_class=ftplib.FTP,
        port=args.port,
        use_passive_mode=False,
        encrypt_data_channel=True,
        encoding=None,
        debug_level=None)
elif args.mode == "passive":
    my_session_factory = session.session_factory(
        base_class=ftplib.FTP,
        port=args.port,
        use_passive_mode=True,
        encrypt_data_channel=True,
        encoding=None,
        debug_level=None)
else:
    print(f"An incorrect string has been passed as the --mode argument.\n"
          f"The string passed was: {args.mode}\n"
          f"The --mode argument only accepts either: active or passive."
          )
    sys.exit(1)

# connect to the ftp site using the passed args and session factory
with ftputil.FTPHost(args.host, args.user, args.pw, session_factory=my_session_factory) as ftp_host:
    # check if the remote file the user wants to download exists on the ftp site
    if ftp_host.path.isfile(args.rdir):
        # if the remote file exists then download it to local location
        print(f"The remote file {args.rdir} exists.")
        ftp_host.download(args.rdir, args.ldir)
        # check if the local file exists to make sure the file was downloaded properly.
        if os.path.isfile(args.ldir):
            print(f"Successfully downloaded the remote file: {args.rdir} to local location: {args.ldir}")
        # the file did not download to local machine so quit program
        else:
            print(f"The script failed to download the remote file: {args.rdir} "
                  f"to the local location: {args.ldir}, because the local file does not exist.")
            sys.exit(1)
    # if the remote file does not exist then quit the program
    else:
        print(f"The remote file {args.rdir} does not exist.")
        sys.exit(1)

    # close connection to FTP site to end the session
    ftp_host.close()
    print(f"Closed connection to FTP site: {args.host}")

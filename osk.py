#!/usr/bin/python3

# Created by    : Ilham Solehudin
# Description   : Os-check
# How to        : os.py -f "filejson"
# Information   :  Auto exec command ssh

import sys, getopt, paramiko
import json

import socket
import time
from colorama import init, Fore


init()

GREEN = Fore.GREEN
RED   = Fore.RED
RESET = Fore.RESET
BLUE  = Fore.BLUE

def is_ssh_open(hostname, username, password):
    print('try ssh connection ' + hostname)
    print('password : ' + password)
    # initialize SSH client
    client = paramiko.SSHClient()
    # add to know hosts
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, username=username, password=password, timeout=3)
    except socket.timeout:
        # this is when host is unreachable
        message = f"[!] Host: {hostname} is unreachable, timed out."
        print(f"{RED}{message}{RESET}")
        return False ,None , message
    except paramiko.AuthenticationException:
      
        message = f"[!] Invalid credentials for {username}:{password}"
        print(message)
        return False ,None, message
    except paramiko.ssh_exception.NoValidConnectionsError:
        message = f"[!] NoValidConnectionsError {hostname} {username}:{password}"
        print(message)
        return False ,None, message
    except paramiko.SSHException:
        print(f"{BLUE}[*] Quota exceeded, retrying with delay...{RESET}")
        # sleep for a minute
        time.sleep(60)
        return is_ssh_open(hostname, username, password)


    else:
        # connection was established successfully
        print(f"{GREEN}[+] Found combo:\n\tHOSTNAME: {hostname}\n\tUSERNAME: {username}\n\tPASSWORD: {password}{RESET}")
        return True , client , "Connected"

def main(argv) :
  
  outputFile = "output.json"
  logFile = "error_output.json"
  
  try:
      print("Runing....")
      opts, args = getopt.getopt(argv,"f:o:l:",["file=","output=","logs="])

  except getopt.GetoptError:
      print('osk.py -f "location.json" -o "pathOutput.json" -l "logs.json"' )
      sys.exit(2)
      
  for opt, arg in opts:
      print(opt)
      if opt == '-h' :
        print("osk.py -f <file> -o <outPath.json> -l <logPath.json>")
        sys.exit()
      elif opt in ("-o", "--output") :
        outputFile = arg
      elif opt in ("-l" , "--logs") :
        logFile = arg
      elif opt in ("-f", "--file") : 
        pathFile = arg
  # outfile
  print("output  : " + outputFile)
  print("logFile  : " + logFile)
  print("pathfile  : " + pathFile)

  # load file
  f = open(pathFile)
  
  # load json
  data = json.load(f)
  
  #  get data parse 
  username = data['username']
  brutePassword = data['brutePassword']
  ssh_command = data['commands']
  machines = data['machines'];
  
  # initial output
  outputs = []
  errorOuputs = []
  
    # loop machines
  for m in machines:
      # loop machine connect
      print ('----------------------------------------')
      # initial object
      o = {"hostname" : m['hostname'], "data" : []}
      
  
  
      # loop password
      for password in brutePassword:    
        ssh_stdin = ssh_stdout = ssh_stderr = None
        okOpen, ssh, msg= is_ssh_open( m['hostname'], username, password) 
        # ssh OK
        if okOpen :
          # exec command payload 
          ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(ssh_command)
          ssh_stdout.channel.recv_exit_status()
          # initial data
          arr_line = []
          if ssh_stdout:
            print("ssh_stdout")
    
                            
              # loop line console ssh
            for line in ssh_stdout:

                arr_line.append(line.strip('\n'))
            # assignment variable
            

          if ssh_stderr:
            print("ssh_stderr")

            for line in ssh_stderr:
                arr_line.append(line.strip('\n'))
                
                
          o['data'] = arr_line
          print(o)
          outputs.append(o)

          # save output
          ssh.close()
          break
        else:
          
          errorOuputs.append({"hostname" : m['hostname'] , "password" : password , "message" : msg});
          
          # save erorr
          with open(logFile, "w") as outfile:
              json.dump(errorOuputs, outfile)

          
        
  with open(outputFile, "w") as outfile:
      json.dump(outputs, outfile)  
  f.close()
if __name__ == "__main__":
    main(sys.argv[1:])
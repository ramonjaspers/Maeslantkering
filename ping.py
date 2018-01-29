from platform import system as system_name  # Returns the system/OS name
from os import system as system_call        # Execute a shell command

def ping(ip):
    if system_name().lower()=="windows":    # Checks for system name
        parameters = "-n 1"                 # If windows-> -n 1
    else:
        parameters = "-c 1"                 # If not windows -> -c 1
    if system_call("ping "+parameters+" "+ip) == 0: # Pings client
        status = "Online"
    else:
        status = "Offline"
    return status

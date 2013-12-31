#!/usr/bin/python
#
# monitor ssh and ban
#
import time,re, thread
from src.core import *
from src.smtp import *

monitor_frequency = int(read_config("MONITOR_FREQUENCY"))
ssh_attempts = read_config("SSH_BRUTE_ATTEMPTS")

def ssh_monitor(monitor_frequency):
        while 1:
                # for debian base
                if os.path.isfile("/var/log/auth.log"):
                        fileopen1 = file("/var/log/auth.log", "r")

        		# for OS X
 		        if os.path.isfile("/var/log/secure.log"):
        		    fileopen1 = file("/var/log/secure.log", "r")

                # for centOS
                if os.path.isfile("/var/log/secure"):
                    fileopen1 = file("/var/log/secure", "r")

                # for Debian
                if os.path.isfile("/var/log/faillog"):
                    fileopen1 = file("/var/log/faillog", "r")

                if not os.path.isfile("/var/artillery/banlist.txt"):
                                # create a blank file
                                filewrite = file("/var/artillery/banlist.txt", "w")
                                filewrite.write("")
                                filewrite.close()

                try:
                        # base ssh counter to see how many attempts we've had
                        ssh_counter = 0
                        counter = 0
                        for line in fileopen1:
                            counter = 0
                            fileopen2 = file("/var/artillery/banlist.txt", "r")
                            line = line.rstrip()
                            # search for bad ssh
                            match = re.search("Failed password for", line)
                            if match:
                                ssh_counter = ssh_counter + 1
                                line = line.split(" ")
                                # pull ipaddress
                                ipaddress = line[10]
                                if is_valid_ipv4(ipaddress):

                                        # if its not a duplicate then ban that ass
                                        if ssh_counter >= int(ssh_attempts):
                                                banlist = fileopen2.read()
                                                match = re.search(ipaddress, banlist)
                                                if match:
                                                        counter = 1
                                                        # reset SSH counter
                                                        ssh_counter = 0

                                                # if counter is equal to 0 then we know that we need to ban
                                                if counter == 0:
                                                        whitelist_match = is_whitelisted_ip(ipaddress)
                                                        if whitelist_match == 0:
                                                                subject = "[!] Artillery has banned an SSH brute force. [!]"
                                                                alert = "Artillery has blocked (blacklisted) the following IP for SSH brute forcing violations: " + ipaddress
                                                                warn_the_good_guys(subject, alert)

                                                                # do the actual ban, this is pulled from src.core
                                                                ban(ipaddress)
                                                                ssh_counter = 0

                                                                # wait one to make sure everything is caught up
                                                                time.sleep(1)
                        # sleep for defined time
                        time.sleep(monitor_frequency)

                except Exception, e:
                    print "[*] An error occured. Printing it out here: " + str(e)

if is_posix():
        thread.start_new_thread(ssh_monitor,(monitor_frequency,))

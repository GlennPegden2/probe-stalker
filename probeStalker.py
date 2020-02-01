import re, os, sys, signal, threading, time, subprocess, argparse, csv
from wigle import Wigle
from subprocess import Popen, PIPE
from colorclass import Color
from terminaltables import AsciiTable
from mac_vendor_lookup import MacLookup


parser = argparse.ArgumentParser()
parser.add_argument("--iface", help='Interface to capture data', required=True)
parser.add_argument("--debug", help='Enable debug', required=False ,  action='store_true')
parser.add_argument("--cont", help='load previous', required=False ,  action='store_true')
args = parser.parse_args()

macdb = MacLookup()
macdb.load_vendors()

run = True
wigle_flag = False
if Wigle.AUTH == '':
    wigle_flag = True

def signal_handler(sig, frame):
    global run
    run = False
    print('Bye! ;)')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def print_data():
    while run:
#        table = AsciiTable(sorted(data, key=lambda x: x[4]))
        table = AsciiTable(sorted(datawithloc, key=lambda x: x[2]))
        if args.debug:
            input("")

        os.system("clear")
        print("Probe Stalker by Glenn Pegden 2019  (based on Probe-Hunter - (c) mgp25 - https://github.com/mgp25/Probe-Hunter)")
        print("{} locations found. {} new".format(len(registeredSSID)+len(registered),len(registered)))
        print(table.table+"\n\n")
        if args.debug:
            time.sleep(20)
        else:
            time.sleep(5)




def check_vendor(macaddr):
    try:
      r = macdb.lookup(macaddr)
    except:
      r = "Unknown ("+macaddr+")"

    return r 

def signal_power(signal):
    if signal <= -70:
        return Color("{autored}"+str(signal)+"{/autored}")
    elif signal > -70 and signal < -55:
        return Color("{autoyellow}"+str(signal)+"{/autoyellow}")
    else:
        return Color("{autogreen}"+str(signal)+"{/autogreen}")

data = []
registered = {}
registeredSSID = {}
datawithloc = []



data.append([Color("{autogreen}SSID{/autogreen}"), Color("{autogreen}Last known client vendor{/autogreen}"), Color("{autogreen}MAC Count{/autogreen}"),Color("{autogreen}Coords. (Lat-Long){/autogreen}"), Color(" {autogreen}Address{/autogreen} ")])
datawithloc.append([Color("{autogreen}SSID{/autogreen}"), Color("{autogreen}Coords. (Lat-Long){/autogreen}"), Color(" {autogreen}Address{/autogreen} ")])

if args.cont:
    with open('loclog.csv', newline='') as csvfile:
        hits = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in hits:
            print(', '.join(row))
            (ssid, company, maccount, loc, adr) = row
            if ssid not in registeredSSID:
                registeredSSID[ssid] = []
                registeredSSID[ssid].append(ssid)

                data.append([ssid, company, maccount, loc, adr])
                datawithloc.append([ssid, loc, adr])

            if ssid not in registered:
                registered[ssid] = []



process = Popen('tcpdump -l -I -i '+args.iface+' -e -s 256 type mgt subtype probe-req', bufsize=1, universal_newlines=True, shell=True, stdout=PIPE, stderr=PIPE)
threading.Thread(target=print_data).start()

for row in iter(process.stdout.readline, b''):
    groups = re.search("Mb\/s (\d+) .* (-\d+)dBm signal .* SA:(\w{2}:\w{2}:\w{2}:\w{2}:\w{2}:\w{2}) .* Probe Request .(.+)\) \[.", row.strip())

#        print(row.strip())

    if groups != None:
        signal = signal_power(int(groups.group(2)))
        mac = groups.group(3)
        ssid = groups.group(4)
        company = check_vendor(mac)

        if args.debug:
            print("Hits from "+mac+" ("+company+") for "+ssid)

        if not ssid in registered and not ssid in registeredSSID:
            registered[ssid] = []
            registered[ssid].append(mac)
            if args.debug:
               print("Looking for {}".format(ssid)) 
            wigle = Wigle.wigle_location(ssid, wigle_flag)
            adr = "~"
            if wigle is  1:
                loc = "API returned error"
                print("API returned error")
            elif wigle is 2 and not wigle_flag:
                loc = '-'
            elif wigle is 3 and not wigle_flag:
                loc = 'API limit reached - Loc faked'
                adr = OSM.OSM_location("53.7581", "-1.6363")
            elif wigle is None and not wigle_flag:
                loc = 'API call failed (nothing returned)'
            elif wigle_flag:
                loc = 'Wigle API Disabled'
            else:
                loc = str(wigle['trilat'])+', '+str(wigle['trilong'])
                adr = str(wigle['road'])+', '+str(wigle['city'])+', '+str(wigle['region'])+', '+str(wigle['postalcode'])
                if adr != "~":
                    maccount = len(registered[ssid])
                    datawithloc.append([ssid, loc, adr])
                    f = open("loclog.csv", "a")
                    f.write("\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"\n".format(ssid, company, str(maccount), loc, adr))
                    f.close()
                    if args.debug:
                        print("Found {} is from {}".format(ssid,adr))			

            maccount = len(registered[ssid])
            data.append([ssid, company, str(maccount), loc, adr])



        elif not mac in registered[ssid]:
            registered[ssid].append(mac)
            mc = len(registered[ssid])

            for sublist in data:
                if ssid in sublist:
                    sublist[2] = str(mc)

        for sublist in data:
            if ssid in sublist:
                sublist[1] = company

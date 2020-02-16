# probe-stalker
Analyses wifi probes (from mobile phones etc) and looks them up on wigle to provide possibly commonly visited locations of people near you

Originally written for a talk on OSINT / Personal Data Leakage at SBG Tech Fest

Based on Probe-Hunter - https://github.com/mgp25/Probe-Hunter

## Requirements

* Python 3
* Linux and a wlan device that can be put into monitor mode

Other requirements are handled with pip

## Setup

1. (optionally) create a virtual environment to work in with `virtualenv venv && source venv/bin/activate`
2. install requirements with `pip3 install -r requirements.txt`
3. edit `.env` to add your wigle.net [api key](https://wigle.net/account)

## Usage

Follow the setup instructions, and then to use the wlan0 interface for sniffing wifi probes run `python probeStalker.py --iface wlan0`
#!/usr/bin/python
#
# dnsrev - Simple DNS PTR generator. Works with IPv4 and IPv6 addresses
# with different zonefile layouts.
#
# Copyright 2011-2016 Wilmer van der Gaast <wilmer@gaast.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

############################### DEPENDENCIES ###############################
# If it doesn't run properly, make sure you have the dnspython and netaddr
# Python modules installed, and named-compilezones. On Debian systems, just
# apt-get install python3-dnspython python3-netaddr bind9utils

#!/usr/bin/env python3

import dns.reversename
import netaddr
import os
import re
import subprocess
import sys
import tempfile
import time
import argparse

AUTO_SEP = ";; ---- dnsrev.py ---- automatically generated, do not edit ---- dnsrev.py ----"

def subnet_rev(full_addr):
    addr, mask = full_addr.split("/")
    full_label = str(dns.reversename.from_address(addr))
    rest = int((128 - int(mask)) / 4) if ':' in addr else int((32 - int(mask)) / 8)
    return full_label.split(".", rest)[-1]

def parse_zone(fn, zone):
    with subprocess.Popen(["/usr/sbin/named-compilezone", "-o", "-", zone, fn],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        zone, errors = p.communicate()
        if p.returncode > 0:
            print(f"While parsing {fn}:\n{errors.decode()}")
            sys.exit(1)
    return zone.decode("utf-8").splitlines()

def dns_re(types):
    return re.compile(r"^([^\s]*\.)\s+(?:\d+\s+)?IN\s+(%s)\s+(.*)$" % "|".join(types))

class ZoneFile:
    def __init__(self, fn):
        self.fn = fn
        self.mktemp()

    def mktemp(self):
        dir, fn = os.path.split(self.fn)
        self.temp_file = tempfile.NamedTemporaryFile(dir=dir, prefix=(fn + ".")).name

def new_soa(old):
    tm = time.localtime()
    new = (tm.tm_year * 1000000 + tm.tm_mon * 10000 + tm.tm_mday * 100)
    return new if new > old else old + 1

def load_config(cfg_file):
    try:
        with open(cfg_file) as f:
            code = compile(f.read(), cfg_file, 'exec')
            cfg = {}
            exec(code, cfg)
            return cfg
    except IOError:
        print(f"Error: Could not open configuration file {cfg_file}")
        sys.exit(1)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Autogen/refresh reverse DNS zonefiles.')
    parser.add_argument('-c', '--config', default='dnsrev.conf', help='Configuration file location (default: ./dnsrev.conf)')
    parser.add_argument('-n', '--dry-run', action='store_true', help='Dry run')
    parser.add_argument('-d', '--diff', action='store_true', help='Show diffs of changes')
    parser.add_argument('-s', '--no-soa-update', action='store_true', help='Do not update SOA serial number')
    return parser.parse_args()

def main():
    args = parse_arguments()
    cfg = load_config(args.config)

    # Further processing based on cfg and args...
    # The rest of the functionality would be implemented here, following the structure and logic of the original script.

if __name__ == "__main__":
    main()

#!/usr/bin/env python

####
#
#       RAWR - Rapid Assessment of Web Resources
#               Written 2012 by Adam Byers  (@al14s)
#                   al14s@pdrcorps.com
#
#
#                      Romans 5:6-8
#
#    See the file 'docs/LICENSE' for copying permission.
#
####

import optparse
from time import sleep
from glob import glob
from platform import system
from lxml import etree

from lib.banner import *
from conf.settings import *
from lib.functions import *

# Set a few static variables
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
scriptpath = os.path.dirname(os.path.realpath(__file__))
logdir = os.path.realpath("log_%s_rawr" % timestamp)


# pull&parse our commandline args
parser = optparse.OptionParser(usage=usage, version=VERSION)
parser.add_option('-a',
                  help='Include all open ports in .csv, not just web interfaces. Creates a threat matrix as well.',
                  dest='allinfo', action='store_true', default=False)
#parser.add_option('-c', metavar="<file>",
#                  help='Specify RAWR .db file from previous enumeration.' +
#                       ' Will run same scan as before, producing same output + a comparison HTML report.',
#                  dest='compfile')
parser.add_option('-f', metavar="<file>",
                  help='NMap|Metasploit|Nessus|Nexpose|Qualys|OpenVAS file or directory from which to pull files. '
                  'See README for valid formats. Use quotes when using wildcards. '
                  'ex:  -f "*.nessus" will parse all .nessus files in directory.', dest='xmlfile')
parser.add_option('-i', metavar="<file>",
                  help="Target an input list.  [NMap format] [can't be used with -n]", dest='nmap_il')
parser.add_option('-n', metavar="<range>",
                  help="Target the specified range or host.  [NMap format]", dest='nmaprng')
parser.add_option('-m', help="Take any inputs, create an Attack Surface Matrix, and exit.",
                  dest='asm', action='store_true', default=False)
parser.add_option('-p', metavar="<port(s)>",
                  help="Specify port(s) to scan.   [default is '80,443,8080,8088']", dest='ports')
parser.add_option('-s', metavar="<port>",
                  help='Specify a source port for the NMap scan.', dest='sourceport', type='int')
parser.add_option('-t', metavar="(1-5)",
                  help='Set a custom NMap scan timing.   [default is 4]', dest='nmapspeed', type='int')
parser.add_option('-v', help='Verbose - Shows messages like spider status updates.',
                  dest='verbose', action='store_true', default=False)
parser.add_option('-y', help='', dest='y', action='store_true', default=False)
parser.add_option('--sslv', help='Assess the SSL security of each target.  [considered intrusive]', dest='sslopt',
                  action='store_true', default=False)

group = optparse.OptionGroup(parser, "Enumeration Options")
group.add_option('-b', help='Use Bing to gather external hostnames. (good for shared hosting)', dest='bing_dns',
                 action='store_true', default=False)
group.add_option('-o', help="Make an 'OPTIONS' call to grab the site's available methods.", dest='getoptions',
                 action='store_true', default=False)
group.add_option('-r', help='Make an additional web call to get "robots.txt"', dest='getrobots', action='store_true',
                 default=False)
group.add_option('-x', help='Make an additional web call to get "crossdomain.xml"',
                 dest='getcrossdomain', action='store_true', default=False)
group.add_option('--downgrade', help='Make requests using HTTP 1.0', dest='ver_dg', action='store_true', default=False)
group.add_option('--noss', help='Disable screenshots.', dest='noss', action='store_true', default=False)
group.add_option('--proxy', metavar="<ip:port>",
                 help="<ip:port> Use Burp/Zap/W3aF to feed credentials to all sites.  " +
                 "** Recommended only for internal sites **", dest='proxy_dict')
group.add_option('--spider', help="Enumerate all urls in target's HTML, create site layout graph.  " +
                 "Will record but not follow links outside of the target's domain." +
                 "  Creates a map (.png) for that site in the <logfolder>/maps folder.",
                 dest='crawl', action='store_true', default=False)
group.add_option('--spider-opts', metavar="<options>", help="Provide custom settings for crawl.               " +
                 "s='follow subdomains',d=depth, l='url limit', t='crawl timeout', u='url timeout', th='thread limit'" +
                 "        Example: --spider-opts s:false,d:2,l:500,th:1",
                 dest='crawl_opts')
group.add_option('--alt-domains', metavar="<domains>",
                 help="Enable cross-domain spidering on specific domains. (comma-seperated)",
                 dest='alt_domains')
group.add_option('--blacklist-urls', metavar="<file>",
                 help="Blacklist specific urls during crawl. Requires a line-seperated input list.",
                 dest='spider_url_blacklist')
parser.add_option_group(group)

group = optparse.OptionGroup(parser, "Output Options")
group.add_option('-d', metavar="<folder>",
                 help='Directory in which to create log folder [default is "./"]', dest='logdir')
group.add_option('-q', '--quiet', help="Won't show splash screen.", dest='quiet', action='store_true', default=False)
group.add_option('-z', help='Compress log folder when finished.',
                 dest='compress_logs', action='store_true', default=False)
group.add_option('--sqlite', help='Put output into an additional sqlite3 db file.', dest='sqlite', action='store_true',
                 default=False)
group.add_option('--json', help='stdout will include only JSON strings. Log folders and files are created normally.',
                 dest='json', action='store_true', default=False)
group.add_option('--json-min', help='The only output of this script will be JSON strings to stdout.',
                 dest='json_min', action='store_true', default=False)
group.add_option('--parsertest', help='Will parse inputs, display the first 3, and exit.', dest='parsertest',
                 action='store_true', default=False)
parser.add_option_group(group)

group = optparse.OptionGroup(parser, "Report Options")
group.add_option('-e', help='Exclude default username/password data from output.', dest='defpass', action='store_false',
                 default=True)
group.add_option('--logo', metavar="<file>", help='Specify a logo file for the HTML report.', dest='logo')
group.add_option('--title', metavar='"Title"', help='Specify a custom title for the HTML report.', dest='title')
parser.add_option_group(group)

group = optparse.OptionGroup(parser, "Update Options")
group.add_option('-u', help='Check for newer version of IpToCountry.csv and defpass.csv.', dest='update',
                 action='store_true', default=False)
group.add_option('-U', help='Force update of IpToCountry.csv and defpass.csv.', dest='forceupdate', action='store_true',
                 default=False)
group.add_option('--check-install', help="Update IpToCountry.csv and defpass.csv. Check for presence of NMap and"
                                         " its version. Check for presence of phantomJS, prompts if installing.",
                 dest='checkinstall', action='store_true', default=False)
group.add_option('--force-install', help="Force update - IpToCountry.csv, defpass,csv, phantomJS.  "
                                         "Also check for presence of NMap and its version.",
                 dest='forceinstall', action='store_true', default=False)
parser.add_option_group(group)

(opts, args) = parser.parse_args()

if opts.y:
    import random
    i = words.split(':')
    e = "%s %s of %s %s" % (random.choice(i[0].split(',')), random.choice(i[1].split(',')),
                            random.choice(i[2].split(',')), random.choice(i[3].split(',')))
    e = (" "*((18-len(e)/2)))+e+(" "*((18-len(e)/2)))
    print(banner.replace("  Rapid Assessment of Web Resources ", e[0:36]))
    sys.exit()

# Remove the big dinosaur...  :\
if not (opts.quiet or opts.json or opts.json_min):
    print(banner)

if len(sys.argv) == 99:
    print(usage)
    sys.exit(2)

if opts.alt_domains:
    opts.alt_domains = opts.alt_domains.split(',')

else:
    opts.alt_domains = []

# Look for PhantomJS if needed
if inpath("phantomjs"):
    pjs_path = "phantomjs"

elif os.path.exists("%s/data/phantomjs/bin/phantomjs" % scriptpath):
    pjs_path = "%s/data/phantomjs/bin/phantomjs" % scriptpath

elif system() in "CYGWIN|Windows" and inpath("phantomjs.exe"):
    pjs_path = "phantomjs.exe"

elif system() in "CYGWIN|Windows" and (os.path.exists("%s/data/phantomjs/phantomjs.exe" % scriptpath)):
    pjs_path = "%s/data//phantomjs/phantomjs.exe" % scriptpath

else:
    pjs_path = ""


if opts.update or opts.forceupdate:
    if opts.update:
        update(False, False, pjs_path, scriptpath)

    else:
        update(True, False, pjs_path, scriptpath)

if opts.forceinstall:
    update(True, True, pjs_path, scriptpath)

elif opts.checkinstall:
    update(False, True, pjs_path, scriptpath)


if pjs_path == "" and not opts.noss:
    print("  " + TCOLORS.RED + "[x]" + TCOLORS.END +
          " phantomJS not found in $PATH or in RAWR folder.  \n\n\tTry running 'rawr.py --check-install'\n\n\tOr"
          " run rawr without screenshots (--noss)\n\n  " + TCOLORS.RED + "[x]" + TCOLORS.END + " Exiting... !!\n\n")
    sys.exit(1)

opts.compfile = None  # for now

# sanity checks
if sum(map(bool, [opts.nmap_il, opts.nmaprng, opts.xmlfile, opts.compfile])) > 1:
    parser.error("  " + TCOLORS.RED + "[x]" + TCOLORS.END + " Can't use -c, -f, -i, or -n in the same command.")
    sys.exit(1)

# Take a look at our inputs
if opts.compfile:
    # check if actual RAWR sqlite3 db output
    if not True:
        parser.error("  " + TCOLORS.RED + "[x]" + TCOLORS.END + " -c <file> must be a RAWR sqlite3 db file.")
        sys.exit(1)

elif opts.xmlfile:
    ftemp = []
    if type(opts.xmlfile) == list:   # it's a list
        for f in opts.xmlfile:
            ftemp.append(f)

    elif os.path.isdir(opts.xmlfile):  # it's a directory
        for f in glob("%s/*" % opts.xmlfile):
            if os.path.isfile(f) and f.split('.')[-1] in ('xml', 'csv', 'nessus'):
                ftemp.append(f)

    elif "," in opts.xmlfile:  # CSV list of files
        ftemp = opts.xmlfile.split(',')

    elif "*" in opts.xmlfile:  # glob it!
        ftemp = glob(opts.xmlfile)

    else:  # glob it!
        ftemp.append(opts.xmlfile)

    files = []
    for f in ftemp:
        if not os.path.isfile(os.path.abspath(f)):  # path not found
            print("\n\n\n  " + TCOLORS.RED + "[x]" + TCOLORS.END + " Unable to locate: \n\t%s\n" % os.path.abspath(f))

        else:
            files.append(os.path.abspath(f))

    if len(files) < 1:
        print("\n  " + TCOLORS.RED + "[x]" + TCOLORS.END + "  No usable files specified. \n")
        sys.exit(1)

elif opts.nmap_il or opts.nmaprng:
    if opts.nmap_il:
        if os.path.exists(opts.nmap_il): 
            nmap_il = os.path.realpath(opts.nmap_il)
        else:
            print("  " + TCOLORS.RED + "[x]" + TCOLORS.END + " Unable to locate file \n  [%s]. =-\n" % opts.nmap_il)
            sys.exit(1)

    else:
        nmaprng = opts.nmaprng

    if opts.ports:
        if str(opts.ports).lower() == "fuzzdb":
            ports = fuzzdb

        elif str(opts.ports).lower() == "all":
            ports = "1-65535"

        else:
            ports = str(opts.ports)

    if opts.nmapspeed:
        try:
            if 6 > int(opts.nmapspeed) > 0:
                nmapspeed = opts.nmapspeed
            else:
                raise()
        except:
            print("\n  " + TCOLORS.RED + "[x]" + TCOLORS.END + "  Scan Timing (-t) must be numeric and 1-5 \n")
            sys.exit(1)

else:
    print(usage + "\n\n\n  " + TCOLORS.RED + "[x]" + TCOLORS.END + "  No input specified. \n")
    sys.exit(1)


if opts.logdir:
    # redefine logdir based on user request
    logdir = os.path.realpath(opts.logdir) + "/log_%s_rawr" % timestamp

#elif platform.machine() == "armv7":
#    logdir = "?"


logfile = "%s/rawr_%s.log" % (logdir, timestamp)

if opts.json_min:
    newdir = False

else:
    # Create the log directory if it doesn't already exist.
    if not os.path.exists(logdir): 
        os.makedirs(logdir)
        newdir = True
    else:
        newdir = False

    os.chdir(logdir)

opts.spider_follow_subdomains = spider_follow_subdomains
opts.spider_depth = int(spider_depth)
opts.spider_timeout = int(spider_timeout)
opts.spider_url_timeout = int(spider_url_timeout)
opts.spider_url_limit = int(spider_url_limit)
opts.spider_thread_limit = int(spider_thread_limit)
# opts.spider_url_max_hits = spider_url_max_hits

try:
    if opts.crawl_opts:
        for o in opts.crawl_opts.split(','):
            a, v = o.split(':')
            if a == "s":
                if v.lower() in ("false", "f"):
                    opts.spider_follow_subdomains = False
                    writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END +
                             " spider_follow_subdomains set to 'False'", logfile, opts)

                elif v.lower() in ("true", "t"):
                    opts.spider_follow_subdomains = True
                    writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END +
                             " spider_follow_subdomains set to 'True'", logfile, opts)

            elif a == "d" and int(v) in range(0, 999):
                opts.spider_depth = int(v)
                writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + " spider_depth set to '%s'" %
                         v, logfile, opts)

            elif a == "t" and int(v) in range(0, 999):
                opts.spider_timeout = int(v)
                writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + " spider_timeout set to '%s'" %
                         v, logfile, opts)

            elif a == "th" and int(v) in range(0, 999):
                opts.spider_thread_limit = int(v)
                writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + " spider_thread_limit set to '%s'" %
                         v, logfile, opts)

            elif a == "l" and int(v) in range(0, 9999):
                opts.spider_url_limit = int(v)
                writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + " spider_url_limit set to '%s'" %
                         v, logfile, opts)

            elif a == "u" and int(v) in range(0, 9999):
                opts.spider_url_timeout = int(v)
                writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + " spider_url_timeout set to '%s'" %
                         v, logfile, opts)

            # elif a == "h" and int(v) in range(0, 999):
            #        opts.spider_url_max_hits = int(v)
            #        writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END +
            #  " spider_url_max_hits set to '%s'" % v, logfile, opts)

except Exception, ex:
    print("      " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " Error with --spider_opts:  '%s'\n\n\t\t%s" %
          (opts.crawl_opts, ex))
    exit()

if opts.logo:
    if os.path.exists(os.path.abspath(opts.logo)):
        try:
            from PIL import Image
            l, h = Image.open(os.path.abspath(opts.logo)).size
            if l > 400 or h > 80:
                writelog("  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                         "  The specified logo may not show up correctly.\n\tA size no larger than 400x80 is "
                         "recommended.\n", logfile, opts)

        except:
            pass  # being able to check the l,h not worth *requiring* that PIL be installed

        logo_file = os.path.realpath(opts.logo)

    else:
        print("\t  " + TCOLORS.RED + "[x]" + TCOLORS.END + "  Unable to locate logo file \n\t\t[%s] \n" % opts.logo)
        sys.exit(1)


if opts.title:
    if len(opts.title) > 60:
        writelog("  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                 " warning The title specified might not show up properly.", logfile, opts)

    report_title = opts.title


# Check for the list of default passwords
if opts.defpass:
    if os.path.exists("%s/%s" % (scriptpath, DEFPASS_FILE)):
        writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + " Located defpass.csv\n", logfile, opts)

    else:
        writelog("  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " Unable to locate %s. =-\n" %
                 DEFPASS_FILE, logfile, opts)
        choice = raw_input("\tContinue without default password info? [Y|n] ").lower()
        defpass = False
        if (not choice in "yes") and choice != "":
            print("\n  " + TCOLORS.RED + "[x]" + TCOLORS.END + " Exiting... \n\n")
            sys.exit(2)

# Check for the IpToCountry list
if os.path.exists("%s/%s" % (scriptpath, IP_TO_COUNTRY)):
    writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + " Located IpToCountry.csv\n", logfile, opts)

else:
    writelog("  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " Unable to locate %s. =-\n" % IP_TO_COUNTRY, logfile, opts)
    choice = raw_input("\tContinue without Ip to Country info? [Y|n] ").lower()
    defpass = False
    if (not choice in "yes") and choice != "":
        print("\n  " + TCOLORS.RED + "[x]" + TCOLORS.END + " Exiting... \n\n")
        sys.exit(2)

if not opts.json_min:
    msg = "\nStarted RAWR : %s\n     cmdline : %s\n\n" % (timestamp, " ".join(sys.argv))
    open("%s/rawr_%s.log" % (logdir, timestamp), 'a').write(msg)  # Log created
    writelog("\n  " + TCOLORS.CYAN + "[+]" + TCOLORS.END + " Log Folder created :\n      %s \n" %
             logdir, logfile, opts)  # Second log entry


if opts.ver_dg:
    writelog("  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + " Downgrading all requests to HTTP/1.0...\n", logfile, opts)
    import httplib  # requests uses urllib3, which uses httplib...
    httplib.HTTPConnection._http_vsn = 10
    httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'

if opts.proxy_dict:
    opts.proxy_dict = {"http": opts.proxy_dict, "https": opts.proxy_dict}

delthis = False

# Create a list called 'files', which contains filenames of all our .xml sources.
if opts.nmap_il or opts.nmaprng:
    files = []
    # Run NMap to provide discovery [xml] data
    if opts.nmap_il != "" \
        or (re.match('^[a-z0-9]+([\-\.][a-z0-9]+)*\.[a-z]{2,6}(:[0-9]{1,5})?(/.*)?$', opts.nmaprng)
            or (re.match(NMAP_INPUT_REGEX, opts.nmaprng)
            and not re.match('([-][0-9]{1,3}[-])|(([,-].*[/]|[/].*[,-])|([*].*[/]|[/].*[*]))', opts.nmaprng))):
        # ^^ check for valid nmap input (can use hostnames, subnets (ex. 192.168.0.0/24), stars (ex. 192.168.*.*),
        # and split ranges (ex. 192.168.1.1-10,14))
        if not (inpath("nmap") or inpath("nmap.exe")):
            writelog("  " + TCOLORS.RED + "[x]" + TCOLORS.END +
                     " NMap not found in $PATH.  Exiting... \n\n", logfile, opts)
            sys.exit(1)

        # Build the NMap command args
        cmd = ["nmap", "-Pn"]

        if opts.sourceport:
            cmd += "-g", str(opts.sourceport)

        sslscripts = "--script=ssl-cert"
        if opts.sslopt:
            sslscripts += ",ssl-enum-ciphers"

        if opts.json_min:
            outputs = "-oX"
            fname = "rawr_" + timestamp + ".xml"

        else:
            outputs = "-oA"
            fname = "rawr_" + timestamp

        proc = subprocess.Popen(['nmap', '-V'], stdout=subprocess.PIPE)
        ver = proc.stdout.read().split(' ')[2]

        # greatly increases scan speed, introduced in nmap v.6.4
        if float(ver) > 6.3:
            cmd += "--max-retries", "0"

        cmd += "-p", ports, "-T%s" % nmapspeed, "-vv", "-sV", sslscripts, outputs, fname, "--open"

        if opts.nmap_il:
            cmd += "-iL", opts.nmap_il

        else:
            cmd.append(opts.nmaprng)

        writelog("  " + TCOLORS.GREEN + "[>]" + TCOLORS.END + " Scanning >\n      " + " ".join(cmd), logfile, opts)

        # need to quiet this when running with --json & --json-min
        try:
            if not (opts.json_min or opts.json):
                with open("%s/rawr_%s.log" % (logdir, timestamp), 'ab') as log_pipe:
                    ret = subprocess.call(cmd, stderr=log_pipe)

            else:
                with open('/dev/null', 'w') as log_pipe:
                    ret = subprocess.Popen(cmd, stdout=log_pipe, stderr=subprocess.PIPE).wait()

        except KeyboardInterrupt:
            writelog("\n\n  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                     "  Scanning Halted (ctrl+C).  Exiting!   \n\n", logfile, opts)
            sys.exit(2)

        except Exception:
            error = traceback.format_exc().splitlines()
            error_msg("\n".join(error))
            writelog("\n\n  " + TCOLORS.RED + "[x]" + TCOLORS.END + "  Error in scan - %s\n\n" %
                     "\n".join(error), logfile, opts)
            sys.exit(2)

        if ret != 0:
            writelog("\n\n", logfile, opts)
            sys.exit(1)

        files = ["rawr_%s.xml" % timestamp]

    else:
        writelog("\n  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                 " Specified address range is invalid. !!\n", logfile, opts)
        sys.exit(1)


elif newdir:
    # Move the user-specified xml file(s) into the new log directory
    old_files = files
    files = ""
    for filename in old_files:
        shutil.copyfile(filename, "./"+os.path.basename(filename))
        files += filename + ","

    files = files.strip(",").split(",")

if not opts.json_min:
    # Look for and copy any images from previous scans
    if not newdir and not (glob("*.png") or glob("images/*.png")):
        writelog("\n  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                 " No thumbnails found in [%s/]\n      or in [.%s/images/]. **\n" %
                 (os.getcwd(), os.getcwd()), logfile, opts)
        if not opts.noss:
            writelog("      Will take website screenshots during the enumeration. ", logfile, opts)

    else:
        png_files = glob("*.png")
        if not os.path.exists("images") and (not opts.noss or len(png_files) > 0):
            os.mkdir("images")

        for filename in glob("*.png"):
            newname = filename.replace(":", "_")
            os.rename(filename, "./images/%s" % newname)

targets = []
for filename in files:
    writelog("\n  " + TCOLORS.GREEN + "[>]" + TCOLORS.END + " Parsing: %s" % filename, logfile, opts)
    c = 0
    try:
        if filename.endswith(".csv"):
            with open(filename) as r:
                head = ' '.join([r.next() for x in xrange(2)])

            if 'Asset Group:' in head:
                for target in parse_qualys_port_service_csv(filename):
                    if "http" in target['service_name']:
                        c += 1

                    targets.append(target)

            else:  # generic CSV
                for target in parse_csv(filename):
                    if "http" in target['service_name']:
                        c += 1

                    targets.append(target)

        elif filename.endswith(".nessus"):
            r = etree.parse(filename)

            if len(r.xpath('//NessusClientData_v2')) > 0:
                for target in parse_nessus_xml(r):
                    if "http" in target['service_name']:
                        c += 1

                    targets.append(target)

            else:
                writelog("  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                         " Unrecognized file format.  [ %s ]" % filename, logfile, opts)
                continue

        elif filename.endswith(".xml"):
            r = etree.parse(filename)

            if len(r.xpath('//NexposeReport')) > 0:
                for target in parse_nexpose_xml(r):
                    if "http" in target['service_name']:
                        c += 1

                    targets.append(target)

            elif len(r.xpath('//NeXposeSimpleXML')) > 0:
                for target in parse_nexpose_simple_xml(r):
                    if "http" in target['service_name']:
                        c += 1

                    targets.append(target)

            elif len(r.xpath('//ASSET_DATA_REPORT')) > 0:
                for target in parse_qualys_scan_report_xml(r):
                    if "http" in target['service_name']:
                        c += 1

                    targets.append(target)

            elif len(r.xpath('//nmaprun')) > 0:
                for target in parse_nmap_xml(r):
                    if "http" in target['service_name']:
                        c += 1

                    targets.append(target)

            elif len(r.xpath('//report[@extension="xml" and @type="scan"]')) > 0:
                for target in parse_openvas_xml(r):
                    if "http" in target['service_name']:
                        c += 1

                    targets.append(target)

            else:
                writelog("      " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                         " Unrecognized file format.\n\n", logfile, opts)
                continue

        else:
            writelog("      " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " Unsupported file type.\n\n", logfile, opts)
            continue

    except Exception:
        error = traceback.format_exc().splitlines()
        error_msg("\n".join(error))
        writelog("      " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " Unable to parse: \n\t\t Error: %s\n\n" %
                 "\n".join(error), logfile, opts)
        continue

    writelog("      " + TCOLORS.CYAN + "[+]" + TCOLORS.END + " Found [ %s ] web interface(s)\n" % c, logfile, opts)

# cleaning up for the --json-min run
if opts.json_min:
    os.remove(files[0])

sqltargets = []
for target in targets:
    if "http" in target['service_name']:
        q.put(target)

    else:
        if opts.allinfo:
            write_to_csv(timestamp, target)

            if opts.sqlite:
                sqltargets.append(target)   # much quicker if we save these up for one call

if opts.parsertest:  # for parser testing.  activated using the --parsertest switch
    for i in xrange(3):
        try:
            print("%s\n" % targets[i])

        except:
            pass

    exit(0)

if opts.sqlite:
    try:
        cmd = 'CREATE TABLE hosts ("%s");' % str('", "'.join(flist.replace('"', "'").split(", ")))
        conn = sqlite3.connect("rawr_%s_sqlite3.db" % timestamp, timeout=10)
        conn.cursor().execute(cmd)
        #cmd = 'CREATE TABLE scans ("id","","","");'
        #conn.cursor().execute(cmd)
        #cmd = 'INSERT INTO meta VALUES ();' % (timestamp, )
        #conn.cursor().execute(cmd)
        conn.commit()
        conn.close()

    except Exception:
        error = traceback.format_exc().splitlines()
        error_msg("\n".join(error))
        output.put("\n  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " Error creating SQLite db:\n\t%s\n" %
                   "\n\t".join(error))
        opts.sqlite = False

    finally:
        conn.close()

if opts.sqlite and opts.allinfo and len(sqltargets) > 0:
    writelog("\n  " + TCOLORS.GREEN + "[>]" + TCOLORS.END + " Populating sqlite db", logfile, opts)
    write_to_sqlitedb(timestamp, targets, opts)

if q.qsize() > 0:
    if not opts.json_min:
        writelog("\n  " + TCOLORS.GREEN + "[>]" + TCOLORS.END + " Building Attack surface matrix", logfile, opts)

        # create our attack surface matrix
        asm_f = "%s/rawr_%s_attack_surface.csv" % (logdir, timestamp)
        cols = []
        hosts = {}
        try:
            for target in targets:
                if 'http' in target['service_name'] or opts.allinfo:
                    if isinstance(target['port'], list):
                        for port in target['port']:
                            cols.append(port)  # populate a list of ports from our targets
                    else:
                        cols.append(target['port'])  # populate a list of ports from our targets

                    try:  # much quicker this way
                        hosts[target['ipv4']][0].append(target['port'])

                    except:
                        hosts[target['ipv4']] = [[target['port']], target['hostnames'][0]]

            #    sort by ipv4 address
            # sorted_x = sorted(x.iteritems(), key=operator.itemgetter(1))
            # import operator
            # hosts.sort(key=lambda hosts: ("%3s%3s%3s%3s" % tuple(operator.itemgetter(1).split('.'))), reverse=False)

            t = {}
            for i in set(cols):
                t[i] = cols.count(i)  # populate a dict with port/count keypairs

            cols = list(set(cols))
            cols.sort(key=int)  # sort cols numerically
            cols.insert(0, "IP")
            cols.insert(1, "HOSTNAME")
            cols.append(" ")
            cols.append("TOTAL")

            with open(asm_f, 'a') as f:
                f.write('"%s"\n' % '","'.join(cols))  # write the column headers

                for host in hosts:    # fill out each line with data from the target
                    line = [" "] * len(cols)
                    line[0] = host
                    line[1] = hosts[host][1]
                    for port in hosts[host][0]:
                        line[cols.index(port)] = "x"

                    line[-1] = (str(line.count("x")))
                    f.write('"%s"\n' % '","'.join(line))

                line = [" "] * len(cols)
                for p in t:
                    line[cols.index(p)] = str(t[p])  # fill out the last line w/ count totals

                line[0] = "TOTAL"

                f.write('\n"%s"\n' % '","'.join(line))

        except Exception:
            error = traceback.format_exc().splitlines()
            error_msg("\n".join(error))
            writelog("\n  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " Error creating attack surface matrix :\n\t%s\n" %
                     "\n".join(error), logfile, opts)

        if opts.asm:  # quit after creating the asm
            exit(0)

    target = None
    targets = None   # it's all in the queue, so we can free up that memory...  :)

    # Begin processing any hosts found
    if not opts.json_min:
        # Create the folder for html resource files
        if not os.path.exists("./html_res"):
            os.makedirs("./html_res")

        shutil.copy("%s/data/jquery.js" % scriptpath, "./html_res/jquery.js")
        shutil.copy("%s/data/style.css" % scriptpath, "./html_res/style.css")
        shutil.copy("%s/data/report_template.html" % scriptpath, 'index_%s.html' % timestamp)

        # Make the link to NMap XML in our HTML report
        if opts.xmlfile:
            fname = os.path.basename(files[0])

        else:
            fname = "rawr_%s.xml" % timestamp

        report_range = ""
        if opts.nmap_il:
            report_range = os.path.basename(str(opts.nmap_il))

        elif opts.nmaprng:
            report_range = str(opts.nmaprng)

        else:
            if type(files) == list:
                if len(files) == 1:
                    report_range = os.path.basename(files[0])

                else:
                    report_range = "%s files" % len(files)

            else:
                report_range = os.path.basename(str(files))

        filedat = open('index_%s.html' % timestamp).read()
        filedat = filedat.replace('<!-- REPLACEWITHLINK -->', fname)
        filedat = filedat.replace('<!-- REPLACEWITHDATE -->', datetime.now().strftime("%b %d, %Y"))
        filedat = filedat.replace('<!-- REPLACEWITHTITLE -->', report_title)
        filedat = filedat.replace('<!-- REPLACEWITHRANGE -->', report_range)
        filedat = filedat.replace('<!-- REPLACEWITHTIMESTAMP -->', timestamp)
        filedat = filedat.replace('<!-- REPLACEWITHFLIST -->', ("hist, " + flist.replace('hist, ', '')))

        if opts.logo:
            shutil.copy(logo_file, "./html_res/")
            l = ('\n<img id="logo" height="80px" src="./html_res/%s" />\n' % os.path.basename(logo_file))
            filedat = filedat.replace('<!-- REPLACEWITHLOGO -->', l)

        open('index_%s.html' % timestamp, 'w').write(filedat)

        if os.path.exists("%s/data/nmap.xsl" % scriptpath):
            if not os.path.exists("./html_res/nmap.xsl"):
                shutil.copy("%s/data/nmap.xsl" % scriptpath, "./html_res/nmap.xsl")

            for xmlfile in glob("rawr_*.xml"):
                    fileloc = re.findall(r'.*href="(.*)" type=.*', open(xmlfile).read())[0]
                    filedat = open(xmlfile).read().replace(fileloc, 'html_res/nmap.xsl')
                    open(xmlfile, 'w').write(filedat)

            writelog("\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END +
                     " Copied nmap.xsl to %s\n\tand updated link in files.\n" % logdir, logfile, opts)

        else:
            writelog("\n  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " Unable to locate nmap.xsl.\n", logfile, opts)

        if not os.path.exists("rawr_%s_serverinfo.csv" % timestamp):
            open("rawr_%s_serverinfo.csv" % timestamp, 'w').write('"' + flist.replace(', ', '","') + '"')

        writelog("\n  " + TCOLORS.GREEN + "[>]" + TCOLORS.END + " Beginning enumeration of [ %s ] host(s)\n" %
                 q.qsize(), logfile, opts)

    # Create the output queue - prevents output overlap
    o = OutThread(output, logfile, opts)
    o.daemon = True
    o.start()

    # Create the main worker pool and get them started
    for i in range(nthreads):
        t = SiThread(timestamp, scriptpath, pjs_path, logdir, output, opts)
        threads.append(t)
        t.daemon = True
        t.start()

    try:
        while q.qsize() > 0:
            sleep(0.5)
            q.join()

    except KeyboardInterrupt:
        print("\n\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END +
              "  ******  Ctrl+C recieved - All threads halted.  ****** \n\n")

    # Queue is clear, tell the threads to close.
    output.put("\n\n  " + TCOLORS.BLUE + "[i]" + TCOLORS.END + "   ** Finished.  Stopping Threads. **\n")

    for t in threads:
        t.terminate = True

    # Close our output queue and clear our main objects
    output.join()
    output = None
    t = None
    o = None
    q = None

    # Add the data and ending tags to the HTML report
    if not opts.json_min:
        open('index_%s.html' % timestamp, 'a').write("</div></body></html>")

        # Sort the csv on the specified column
        try:
            i = flist.lower().split(", ").index(csv_sort_col)
            data_list = [l.strip() for l in open("rawr_%s_serverinfo.csv" % timestamp)]
            headers = data_list[0]
            data_list = data_list[1:]
            # Format IP adresses so we can sort them effectively
            if re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}" +
                        "([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", l.split(",")[i]):
                key = "%3s%3s%3s%3s" % tuple(l.split(",")[i].split('.'))

            else:
                key = l.split(",")[i]

            data_list.sort(key=lambda d: key)
            open("rawr_%s_serverinfo.csv" % timestamp, 'w').write(headers+"\n"+"\n".join(data_list))

        except:
            writelog("\n  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                     " '%s' was not found in the column list.  Skipping the CSV sort function." %
                     csv_sort_col, logfile, opts)

        writelog("\n  " + TCOLORS.CYAN + "[+]" + TCOLORS.END +
                 " Report created in [%s/]\n" % os.getcwd(), logfile, opts)

        if opts.compress_logs:
            writelog("  " + TCOLORS.GREEN + "[>]" + TCOLORS.END + " Compressing logfile...\n", logfile, opts)
            logdir = os.path.basename(os.getcwd())
            os.chdir("../")
            try:
                if system() in "CYGWIN|Windows":
                    shutil.make_archive(logdir, "zip", logdir)
                    logdir_c = logdir + ".zip"
                else:
                    tfile = tarfile.open(logdir+".tar", "w:gz")
                    tfile.add(logdir)
                    tfile.close()
                    logdir_c = logdir + ".tar"

                writelog("  " + TCOLORS.CYAN + "[+]" + TCOLORS.END + " Created  %s ++\n" % logdir_c, logfile, opts)
                if os.path.exists(logdir) and os.path.exists(logdir_c):
                    shutil.rmtree(logdir)

            except Exception:
                error = traceback.format_exc().splitlines()
                error_msg("\n".join(error))
                writelog("  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END +
                         " Failed\n\t%s\n" % "\n\t".join(error), logfile, opts)

else:
    writelog("\n  " + TCOLORS.YELLOW + "[!]" + TCOLORS.END + " No data returned. \n\n", logfile, opts)
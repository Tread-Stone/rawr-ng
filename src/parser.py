from argparse import ArgumentParser, SUPPRESS
from settings import nmapspeed, useragent, report_title


def get_parser():
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("-a", help="Include all open ports in .csv and surface matrix.", action="store_true", dest="all_info")

    parser.add_argument('-m', help="Process inputs, create an Attack Surface Matrix,\n   then exit.", dest='asm',
                    action='store_true')
    parser.add_argument('-p', metavar="<port(s)>", help="Specify port(s) to scan.\n   [default is '80,443,8080,8088']",
                        dest='ports', default='80,443,8080,8088')
    parser.add_argument('-s', metavar="<port>", help='Specify a source port for the NMap scan.', dest='sourceport',
                        type=int)
    parser.add_argument('-t', metavar="(1-5)", help='Set a custom NMap scan timing.   [default is 4]', dest='nmapspeed',
                        type=int, default=nmapspeed)
    parser.add_argument('-u', help='Update - Check for newer version of required files.\n  * Ignores other arguments.',
                        dest='update', action='store_true')
    parser.add_argument('-U', help=SUPPRESS, dest='forceupdate', action='store_true')
    parser.add_argument('-v', help='Verbose - Shows messages like spider status updates.', dest='verbose',
                        action='store_true')
    parser.add_argument('-y', help=SUPPRESS, dest='y', action='store_true')
    parser.add_argument('--sslv', help='Assess the SSL security of each target.\n   [considered intrusive]',
                        dest='sslopt', action='store_true')

    enumeration = parser.add_argument_group(" ENUMERATION")
    enumeration.add_argument('--dns', help='Use Bing for reverse DNS lookups.', dest='dns', action='store_true')
    # group.add_argument('--dorks', help='Use Google filetype: to pull common doctypes.', dest='dorks', action='store_true')
    enumeration.add_argument('-o', help="Make an 'OPTIONS' call to grab the site's available\n methods.", dest='getoptions',
                       action='store_true')
    enumeration.add_argument('-r', help='Make an additional web call to get "robots.txt"', dest='getrobots', action='store_true')
    enumeration.add_argument('-x', help='Make an additional web call to get "crossdomain.xml"', dest='getcrossdomain',
                       action='store_true')
    enumeration.add_argument('--downgrade', help='Make requests using HTTP 1.0', dest='ver_dg', action='store_true')
    enumeration.add_argument('--noss', help='Disable screenshots.', dest='noss', action='store_true')
    enumeration.add_argument('--rd', help='Take screenshots of RDP and VNC interfaces.', dest='rdp_vnc', action='store_true')
    enumeration.add_argument('--proxy', metavar="<[username:password@]ip:port[+type] | filename>",
                       help="Push all traffic through a proxy.\n  Supported types are socks and http," +
                            "basic, digest.\nFile should contain proxy info on one line.\n" +
                            "   example -  'username:password@127.0.0.1:9050+socks'\n", dest='proxy_dict')
    enumeration.add_argument('--proxy-auth', help='Specify authentication for the proxy at runtime with\n getpass.',
                       dest='proxy_auth', action='store_true')
    enumeration.add_argument('--spider', dest='crawl', action='store_true',
                       help="Enumerate all urls in target's HTML, create site layout\n graph." +
                            "  Will record but not follow links outside of\n the target's domain." +
                            "  Creates a map (.png) for that\n site in the <logfolder>/maps folder.")
    enumeration.add_argument('--udp', help='Have NMap check both TCP and UDP during scan.', dest='udp', action='store_true')
    enumeration.add_argument('--alt-domains', metavar="<domains>",
                       help="Enable cross-domain spidering on specific domains.\n  (comma-seperated)", dest='alt_domains')
    enumeration.add_argument('--blacklist-urls', metavar="<file>",
                       help="Blacklist specific urls during crawl. Requires a\n line-seperated input list.",
                       dest='spider_url_blacklist')
    enumeration.add_argument('--mirror', dest='mirror', action='store_true',
                       help="Crawl and create a cached copy of sites, stored in\n the 'mirrored_sites' folder." +
                            "  Note: This will initiate\n a crawl, so --spider is not necessary.\n" +
                            " Any regular spidering options can still be\n  specified using the options above.")
    enumeration.add_argument('--useragent', dest='useragent', metavar="<string|file>",
                       help='Use a custom user agent. Default is in' +
                            " settings.py.\n  Accepts a line-delimited list of useragent strings.\n  ** This will" +
                            " exponentially increase the number\n   of interfaces! **", default=useragent)

    crawl = parser.add_mutually_exclusive_group()
    crawl.add_argument('-S', metavar="(1-5)",
                   help="Use a pre-set crawl aggression level.\n   Levels are listed in settings.py.", dest='crawl_level',
                   type=int)
    crawl.add_argument('--spider-opts', dest='crawl_opts', metavar="<options>",
                   help="Provide custom settings for crawl.\n" +
                        "s='follow subdomains', d=depth, l='url limit'\nt='crawl timeout', u='url timeout'," +
                        " th='thread limit'\n        Example: --spider-opts s:false,d:2,l:500,th:1")

    output = parser.add_argument_group(" OUTPUT")
    output .add_argument('-d', metavar="<folder>", help='Directory in which to create log folder\n   [default is "./"]',
                       dest='logdir')
    output.add_argument('-q', '--quiet', help="Won't show splash screen.", dest='quiet', action='store_true')
    output.add_argument('-z', help='Compress log folder when finished.', dest='compress_logs', action='store_true')
    output.add_argument('--json', help='stdout will include only JSON strings.  Log folders and\n' +
                       ' files are created normally.', dest='json', action='store_true')
    output.add_argument('--json-min', help='The only output of this script will be JSON strings to\n stdout.', dest='json_min',
                       action='store_true')
    output.add_argument('--notify', nargs='?', metavar="email address",
                       help='Send an email or SMS notification via sendmail when\n scan is complete.' +
                            ' Specifying a recipient email address\n is not necessary if one is defined in' +
                            ' settings.py.\n   (Requires configuration in conf/settings.py)', dest='notify')
    output.add_argument('--parsertest', help='Will parse inputs, display the first 3, and exit.', dest='parsertest',
                       action='store_true')

    report = parser.add_argument_group(" REPORTING")
    report.add_argument('-e', help='Exclude default username/password data from output.', dest='defpass',
                       action='store_false', default=True)
    report.add_argument('--logo', metavar="<file>", help='Specify a logo file for the HTML report.', dest='logo')
    report.add_argument('--title', metavar='"Title"', help='Specify a custom title for the HTML report.', dest='title',
                       default=report_title)

    return parser



if __name__ == "__main__":
    parser = get_parser()
    args = vars(parser.parse_args())
    print(args)

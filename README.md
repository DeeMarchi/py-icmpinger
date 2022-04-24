# py-icmpinger
Small implementation of an ICMP echo, in pure Python

This small project is a simple implementation of an ICMP echo request, using raw sockets

**Tested and is working on Windows 10 (Python 3.9), and Linux (Debian distro, using Python 3.7), as of 2022**

## Requirements: Python 3.5 or greater

To use this CLI utility, you need to specify the target IP address, using '-t' or '--target', followed by a domain name or IP address

Eg: **python py-icmpinger.py -t 127.0.0.1** [ADDITIONAL PARAMETERS, without brackets] 

### Additional parameters are
> - --timeout SECONDS
>
> Sets the max timeout value in seconds
>
> - -c or --count PINGS
>
> How many times to ping the host, defaults to 4
>
> -  -d or --delay MILLISECONDS
>
> Time in milliseconds between pings, defaults to 500 (ms)
>
> - -i or --infinite
>
> Pings without stopping, (use CTRL + C to stop)
>
> - -s or --size LENGTH
>
> Size of the payload in bytes (the limit is 65500 bytes)

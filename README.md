# cpremote
cpremote is a command line tool for interacting with a CircuitPython remote filesystem using the web based workflow

# description
This command line tool implements the CircuitPython [web based workflow](https://docs.circuitpython.org/en/latest/docs/workflows.html#web) and is great for
* CircuitPython boards that do not support native USB
* CircuitPython boards that are remote
* Workflows in which a CircuitPython project is kept external from the CircuitPython board such as on a host computer

I use `cpremote`, [`circup`](https://github.com/adafruit/circup) and [`CircuitPython for Visual Studio Code`](https://marketplace.visualstudio.com/items?itemName=joedevivo.vscode-circuitpython)with all of my CircuitPython projects.

# install
```sh
pip install cpremote
```

# environment variables
cpremote will look for a `.env` file in the current directory which can contain the CircuitPython host name, password and/or file size units use with `ls`
```sh
# IP address recommended for better performance
CPREMOTE_HOST=http://192.168.1.90
# remote password
CPREMOTE_PASSWORD=mypassword
# file size units for 'ls' command: 'b' - bytes, 'kb' - kilobytes or 'blocks'
CPREMOTE_UNITS=kb
```

# example command usage

## ls
Show the root directory on the remote filesystem
```sh
cpremote ls
```

## get
Copy `code.py` from the remote filesystem to the console
```sh
cpremote get code.py
```

## put
Copy `code.py` from the local filesystem to the remote filesystem. Note that the CircuitPython board's hostname and password can be set in `.env`, or can be overriden on the command line
```sh
cpremote --host http://1.2.3.4 --password mypassword put code.py
```

## repl
The `repl` command will launch a basic web repl using the default system browser

## help
Full help. Also, note that help for individual command line options is available using `-h` or `--help` before a command
```
cpremote --help
usage: cpremote [-h] [--host HOST] [--password PASSWORD] [--units {b,kb,blocks}] [-v] {devices,diskinfo,get,ls,mkdir,mv,put,repl,rm,rmdir,version} ...

CircuitPython remote filesystem access for web based workflow

positional arguments:
  {devices,diskinfo,get,ls,mkdir,mv,put,repl,rm,rmdir,version}
                        command help
    devices             show info about CircuitPython devices on the local network
    diskinfo            show disk info about the remote filesystem
    get                 get a file from remote filesystem
    ls                  list a directory on the remote filesystem
    mkdir               make a directory on the remote filesystem
    mv                  move (rename) a file or directory on the remote filesystem
    put                 put a file on the remote filesystem
    repl                start Web REPL
    rm                  remove a file on the remote filesystem
    rmdir               remove the directory and all of its contents on the remote filesystem
    version             returns information about the device

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           CircuitPython host name. Overrides CPREMOTE_HOST environment variable
  --password PASSWORD   CircuitPython password.Overrides CPREMOTE_PASSWORD environment variable
  --units {b,kb,blocks}
                        file size units. Overrides CPREMOTE_UNIT environment variable
  -v, --version         show program's version number and exit
```

# IP addresses vs mDNS local host names
In my experience, using IP addresses seems to be more performant than mDNS local host names when accessing a CircuitPython board. However, this may be an issue in my local network so your experience may be different

# Attribution
CircuitPython is created by Adafruit Industries.

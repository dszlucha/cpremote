# MIT License

# Copyright (c) 2024 dszlucha

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import json
import os
import time
import webbrowser

import dotenv
import requests
from requests.auth import HTTPBasicAuth

from . import __version__

def get(src: str, dst: str):
    '''get a file from remote filesystem'''
    basic = HTTPBasicAuth('', cpremote_password)
    response = requests.request('GET', cpremote_host + '/fs/' + src, auth=basic)
    if response.status_code == 200:
        if dst is None:
            print(response.text)
        else:
            with open(dst, 'w', encoding='utf-8') as file:
                file.write(response.text)
            print('File exists and file returned')
    else:
        message = {401: 'Incorrect password',
                   403: 'No CIRCUITPY_WEB_API_PASSWORD set',
                   404: 'Missing file'}
        try:
            print(message[response.status_code])
        except KeyError:
            print(f'Unknown status_code: {response.status_code}')

def info(path: str):
    '''show info about CircuitPython devices on the local network'''
    response = requests.request('GET', cpremote_host + '/cp/' + path + '.json')
    obj = json.loads(response.text)
    json_formatted_str = json.dumps(obj, indent=4)
    print(json_formatted_str)

def ls(directory: str):
    '''list a directory on the remote filesystem'''
    if not directory.endswith('/'):
        directory += '/'
    basic = HTTPBasicAuth('', cpremote_password)
    headers = {'Accept': 'application/json'}
    response = requests.request('GET', cpremote_host + '/fs/' + directory, auth=basic,
                                headers=headers, timeout=5)
    if response.status_code == 200:
        data = response.json()
        files = data['files']
        if directory == '':
            directory = '/'
        print(f'Host {cpremote_host}, directory {directory}')
        print('Size\tModified\tName')
        for file in files:
            directory = '/' if file['directory'] else ''
            current_time = time.localtime()
            t = time.localtime(file['modified_ns']/1000000000)
            modified_time = (time.strftime("%b %d %H:%M", t)
                if
                    t.tm_year == current_time.tm_year
                else
                    time.strftime("%b %d  %Y", t))
            file_size = file['file_size'] if directory == '' else ''
            print(f'{file_size}\t{modified_time}\t{file["name"]}{directory}')
        free = data['free']
        total = data['total']
        block_size = data['block_size']
        if cpremote_units == 'b':
            free = free * block_size
            total = total * block_size
        elif cpremote_units == 'kb':
            free = (free * block_size) / 1024
            total = (total * block_size) / 1024
        print(f'free: {free} {cpremote_units}, total: {total} {cpremote_units}, block size: {block_size}, writable: {data["writable"]}')
    else:
        message = {401: 'Incorrect password',
                   403: 'No CIRCUITPY_WEB_API_PASSWORD set',
                   404: 'Missing directory'}
        try:
            print(message[response.status_code])
        except KeyError:
            print(f'Unknown status_code: {response.status_code}')

def mkdir(directory: str):
    '''make a directory on the remote filesystem'''
    if not directory.endswith('/'):
        directory += '/'
    basic = HTTPBasicAuth('', cpremote_password)
    response = requests.request('PUT', cpremote_host + '/fs/' + directory, auth=basic)
    message = {201: 'Directory created',
               204: 'Directory or file exists',
               401: 'Incorrect password',
               403: 'No CIRCUITPY_WEB_API_PASSWORD set',
               404: 'Missing parent directory',
               409: 'USB is active and preventing file system modification'}
    try:
        print(message[response.status_code])
    except KeyError:
        print(f'Unknown status_code: {response.status_code}')

def mv(src: str, dst: str):
    '''move (rename) a file or directory on the remote filesystem'''
    basic = HTTPBasicAuth('', cpremote_password)
    headers = {'X-Destination': '/fs/' + dst}
    response = requests.request('MOVE', cpremote_host + '/fs/' + src, auth=basic, headers=headers)
    message = {201: 'File/directory renamed',
               401: 'Incorrect password',
               403: 'No CIRCUITPY_WEB_API_PASSWORD set',
               404: 'Source file/directory not found or destination path is missing',
               409: 'USB is active and preventing file system modification',
               412: 'Precondition Failed - The destination path is already in use'}
    try:
        print(message[response.status_code])
    except KeyError:
        print(f'Unknown status_code: {response.status_code}')

def put(src: str, dst: str):
    '''put a file on the remote filesystem'''
    if not os.path.exists(src):
        print(f'File {src} does not exist')
        return
    if dst is None:
        dst = src
    basic = HTTPBasicAuth('', cpremote_password)
    with open(src, 'r', encoding='utf-8') as file:
        data = file.read()
    response = requests.request('PUT', cpremote_host + '/fs/' + dst, auth=basic, data=data)
    message = {201: 'File created and saved',
               204: 'File existed and overwritten',
               401: 'Incorrect password',
               403: 'No CIRCUITPY_WEB_API_PASSWORD set',
               404: 'Missing parent directory',
               409: 'USB is active and preventing file system modification',
               413: 'Expect header not sent and file is too large',
               417: 'Expect header sent and file is too large',
               500: 'Other, unhandled error'}
    try:
        print(message[response.status_code])
    except KeyError:
        print(f'Unknown status_code: {response.status_code}')

def repl():
    '''start Web REPL'''
    webbrowser.open(cpremote_host + '/cp/serial/')

def rm(file: str):
    '''remove a file on the remote filesystem'''
    basic = HTTPBasicAuth('', cpremote_password)
    response = requests.request('DELETE', cpremote_host + '/fs/' + file, auth=basic)
    message = {204: 'File existed and deleted',
               401: 'Incorrect password',
               403: 'No CIRCUITPY_WEB_API_PASSWORD set',
               404: 'File not found',
               409: 'USB is active and preventing file system modification'}
    try:
        print(message[response.status_code])
    except KeyError:
        print(f'Unknown status_code: {response.status_code}')

def rmdir(directory: str):
    '''remove the directory and all of its contents on the remote filesystem'''
    if not directory.endswith('/'):
        directory += '/'
    basic = HTTPBasicAuth('', cpremote_password)
    response = requests.request('DELETE', cpremote_host + '/fs/' + directory, auth=basic)
    message = {204: 'Directory and its contents deleted',
               401: 'Incorrect password',
               403: 'No CIRCUITPY_WEB_API_PASSWORD set',
               404: 'No directory',
               409: 'USB is active and preventing file system modification'}
    try:
        print(message[response.status_code])
    except KeyError:
        print(f'Unknown status_code: {response.status_code}')

def main():
    '''main entry point'''
    global cpremote_host
    global cpremote_password
    global cpremote_units

    config = dotenv.find_dotenv(usecwd=True)
    if config:
        dotenv.load_dotenv(config)
    cpremote_host = os.getenv('CPREMOTE_HOST')
    cpremote_password = os.getenv('CPREMOTE_PASSWORD')
    cpremote_units = os.getenv('CPREMOTE_UNITS')

    parser = argparse.ArgumentParser(
        description='CircuitPython remote filesystem access for web based workflow')
    parser.add_argument(
        '--host', help='CircuitPython host name. Overrides CPREMOTE_HOST environment variable')
    parser.add_argument('--password',
                        help='CircuitPython password.'
                             'Overrides CPREMOTE_PASSWORD environment variable')
    parser.add_argument('--units', choices=['b', 'kb', 'blocks'],
                        help='file size units. Overrides CPREMOTE_UNIT environment variable')
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='command help')

    subparsers.add_parser('devices',
                          help='show info about CircuitPython devices on the local network')
    subparsers.add_parser('diskinfo', help='show disk info about the remote filesystem')

    parser_get = subparsers.add_parser('get', help='get a file from remote filesystem')
    parser_get.add_argument('src', help='source file from remote filesystem')
    parser_get.add_argument('dst', default=None, nargs='?', help='destination file on local '
                            ' filesystem. Outputs to console if not set')

    parser_ls = subparsers.add_parser('ls', help='list a directory on the remote filesystem')
    parser_ls.add_argument('directory', default='/', nargs='?', help='directory to show')

    parser_mkdir = subparsers.add_parser('mkdir', help='make a directory on the remote filesystem')
    parser_mkdir.add_argument('directory', help='directory to make on the remote filesystem')

    parser_mv = subparsers.add_parser('mv', help='move (rename) a file or directory on the remote filesystem')
    parser_mv.add_argument('src', help='source file or directory on remote filesystem')
    parser_mv.add_argument('dst', help='destination file or directory on remote filesystem')

    parser_put = subparsers.add_parser('put', help='put a file on the remote filesystem')
    parser_put.add_argument('src', help='source file from local filesystem')
    parser_put.add_argument('dst', default=None, nargs='?', help='destination file name')

    subparsers.add_parser('repl', help='start Web REPL')

    parser_rm = subparsers.add_parser('rm', help='remove a file on the remote filesystem')
    parser_rm.add_argument('file', help='file to remove from the remote filesystem')

    parser_rmdir = subparsers.add_parser('rmdir', help='remove the directory and all of its '
                                         'contents on the remote filesystem')
    parser_rmdir.add_argument('directory', help='directory to remove from the remote filesystem')

    subparsers.add_parser('version', help='returns information about the device')

    args = parser.parse_args()
    if not args.host is None:
        cpremote_host = args.host
    if not args.password is None:
        cpremote_password = args.password
    if not args.units is None:
        cpremote_units = args.units

    if cpremote_host is None:
        print('Error: CPREMOTE_HOST is not set')
        return

    if cpremote_password is None:
        print('Error: CPREMOTE_PASSWORD is not set')
        return

    if args.command == 'devices':
        info('devices')
    elif args.command == 'diskinfo':
        info('diskinfo')
    elif args.command == 'get':
        get(args.src, args.dst)
    elif args.command == 'ls':
        ls(args.directory)
    elif args.command == 'mkdir':
        mkdir(args.directory)
    elif args.command == 'mv':
        mv(args.src, args.dst)
    elif args.command == 'put':
        put(args.src, args.dst)
    elif args.command == 'repl':
        repl()
    elif args.command == 'rm':
        rm(args.file)
    elif args.command == 'rmdir':
        rmdir(args.directory)
    elif args.command == 'version':
        info('version')
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

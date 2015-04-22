# -*- mode: python; coding: utf-8 -*-
#
# Copyright (c) 2014, 2015 Andrej Antonov <polymorphm@gmail.com>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

assert str is not bytes

import sys
import os, os.path
import argparse
import getpass
import codecs
from . import main_errors
from . import locale_unzip

def main(encoding=None):
    parser = argparse.ArgumentParser(
            description=
                    'utility for unzip files with non-standard encoding name',
            )
    
    parser.add_argument(
            '-d',
            '--exdir',
            metavar='EXDIR',
            help='extract files into EXDIR',
            )
    
    parser.add_argument(
            '--password',
            metavar='PASSWORD-ENV',
            help='system environ name for password. use value ``input`` for interactive input',
            )
    
    parser.add_argument(
            '--password-encoding',
            metavar='PASSWORD-ENCODING',
            help='encoding for password',
            )
    
    if encoding is None:
        parser.add_argument(
                'encoding',
                metavar='ENCODING',
                help='encoding for file names. for example ``cp866`` for cyrillic',
                )
    
    parser.add_argument(
            'zipfile',
            metavar='ZIPFILE-PATH',
            help='path to zipfile',
            )
    
    parser.add_argument(
            'file',
            metavar='FILE-NAME',
            nargs='*',
            help='file to extract from zipfile',
            )
    
    args = parser.parse_args()
    
    try:
        exdir = args.exdir
        
        if args.password == 'input':
            password = getpass.getpass(
                    prompt='password (hidden input): ',
                    )
        elif args.password is not None:
            if args.password not in os.environ:
                raise main_errors.ArgError(
                        'not found system environ: {!r}'.format(args.password),
                        )
            
            password = os.environ[args.password]
        else:
            password = None
        
        if password is not None:
            if args.password_encoding is not None:
                try:
                    # only for check of encoding
                    codecs.lookup(args.password_encoding)
                except LookupError:
                    raise main_errors.ArgError(
                            'can not look up info of codec {!r}'.format(args.password_encoding),
                            )
                
                password = password.encode(args.password_encoding)
            else:
                password = password.encode()
        
        if encoding is None:
            encoding = args.encoding
        zipfile_path = args.zipfile
        if args.file:
            file_name_list = tuple(args.file)
        else:
            file_name_list = None
        
        try:
            # only for check of encoding
            codecs.lookup(encoding)
        except LookupError:
            raise main_errors.ArgError(
                    'can not look up info of codec {!r}'.format(encoding),
                    )
        
        locale_unzip.locale_unzip(
                encoding, zipfile_path, file_name_list,
                exdir=exdir, password=password,
                )
    except main_errors.ArgError as err:
        err_str = str(err)
        print(
                'argument error: {}'.format(err_str),
                file=sys.stderr,
                )
        exit(code=2)
    except main_errors.ProgramError as err:
        err_str = str(err)
        print(
                'program error: {}'.format(err_str),
                file=sys.stderr,
                )
        exit(code=1)

# -*- mode: python; coding: utf-8 -*-
#
# Copyright (c) 2014 Andrej Antonov <polymorphm@gmail.com>.
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

import os, os.path
import zipfile
import time
import calendar
from . import main_errors
from . import safe_run

READ_BUF_SIZE = 1000000
# XXX   big size because each read operation opens own thread

def locale_fix_name(encoding, name):
    assert isinstance(name, str)
    
    try:
        fixed_name = name.encode('cp437').decode(encoding)
    except ValueError:
        return name
    
    return fixed_name

def secure_name(name):
    assert isinstance(name, str)
    
    while True:
        if name.startswith('/') or name.startswith('\\'):
            name = name[1:]
            continue
        
        secured_name = name.replace('../', '__/').replace('..\\', '__\\')
        
        if secured_name != name:
            name = secured_name
            continue
        
        return name

def get_mtime(zinfo):
    raw_mtime = calendar.timegm(zinfo.date_time)
    fixed_mtime = raw_mtime + time.altzone
    
    return fixed_mtime

def check_error(error, prefix=None):
    assert prefix is None or isinstance(prefix, str)
    
    if error is not None:
        error_type, error_str = error
        
        if prefix is not None:
            show_str = '{}: {!r}: {}'.format(prefix, error_type, error_str)
        else:
            show_str = '{!r}: {}'.format(error_type, error_str)
        
        raise main_errors.ProgramError(show_str)

def locale_unzip(encoding, zipfile_path, file_name_list, exdir=None, password=None):
    pid, error = safe_run.safe_run(os.getpid)
    check_error(error)
    
    z, error = safe_run.safe_run(zipfile.ZipFile, zipfile_path)
    
    check_error(error, prefix='opening zipfile')
    
    try:
        if password is not None:
            setpassword_result, error = safe_run.safe_run(z.setpassword, password)
            check_error(error)
            
            print(password)
        
        infolist_result, error = safe_run.safe_run(z.infolist)
        check_error(error)
        
        zinfo_list = tuple(infolist_result)
        
        for zinfo in zinfo_list:
            raw_filename = zinfo.filename
            fixed_filename = secure_name(locale_fix_name(encoding, raw_filename))
            
            if file_name_list is not None and fixed_filename not in file_name_list:
                continue
            
            safe_run.safe_run(print,
                    'unzipping: {!r}'.format(fixed_filename),
                    )
            
            if fixed_filename.endswith('/'):
                is_dir = True
                
                if exdir is not None:
                    w_dir = os.path.join(exdir, fixed_filename[:-1])
                else:
                    w_dir = fixed_filename[:-1]
                w_path = None
                w_new_path = None
            else:
                is_dir = False
                if exdir is not None:
                    w_path = os.path.join(exdir, fixed_filename)
                else:
                    w_path = fixed_filename
                w_dir = os.path.dirname(w_path)
                w_new_path = '{}.new-{}'.format(w_path, pid)
            
            mtime, mtime_error = safe_run.safe_run(get_mtime, zinfo)
            
            safe_run.safe_run(os.makedirs, w_dir)
            
            if is_dir:
                z_fd = None
                w_fd = None
            else:
                z_fd, error = safe_run.safe_run(
                        z.open,
                        raw_filename, mode='r',
                        )
                check_error(error)
                
                try:
                    w_fd, error = safe_run.safe_run(open, w_new_path, 'wb')
                    check_error(error, prefix='writing file')
                    
                    try:
                        while True:
                            buf, error = safe_run.safe_run(z_fd.read, READ_BUF_SIZE)
                            check_error(error)
                            
                            assert isinstance(buf, bytes)
                            
                            write_result, error = safe_run.safe_run(w_fd.write, buf)
                            check_error(error)
                            
                            if not buf:
                                break
                    finally:
                        w_close_result, error = safe_run.safe_run(w_fd.close)
                        check_error(error)
                finally:
                    z_close_result, error = safe_run.safe_run(z_fd.close)
                    check_error(error)
                
                safe_run.safe_run(os.replace, w_new_path, w_path)
                check_error(error)
            
            if mtime_error is None:
                if is_dir:
                    safe_run.safe_run(
                            os.utime,
                            w_dir, (mtime, mtime),
                            )
                else:
                    safe_run.safe_run(
                            os.utime,
                            w_path, (mtime, mtime),
                            )
            if is_dir:
                safe_run.safe_run(print,
                        'dir: {!r}'.format(w_dir),
                        )
            else:
                safe_run.safe_run(print,
                        'writed: {!r}'.format(w_path),
                        )
    finally:
        safe_run.safe_run(z.close)

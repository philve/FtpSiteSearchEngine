# -*- coding: utf-8 -*-

import ftplib
import logging
import threading
import tkinter
from datetime import datetime

def search_ftp(q, ip_list, file_type=None, name_contains=None, date_range=None, min_size=None, max_size=None):
    logging.basicConfig(filename='search.log', level=logging.INFO)
    logging.info('[search module]IP list: %s' % ip_list)

    count = 0
    ftp_data = []

    for i, scan_ip in enumerate(ip_list):
        t = threading.Thread(target=anonymous_scan, args=(scan_ip, file_type, name_contains, date_range, min_size, max_size), name='searchThread' + str(i))
        t.start()
        t.join()
        count += 1
        if count == len(ip_list):
            q.put(ftp_data)
    return True

def anonymous_scan(scan_ip, file_type=None, name_contains=None, date_range=None, min_size=None, max_size=None):
    try:
        ftp = ftplib.FTP(scan_ip, timeout=5)
        ftp.login()
        file_list = ftp.mlsd()
        filtered_files = []

        for f in file_list:
            file_name, file_info = f
            file_mod_datetime = datetime.strptime(file_info['modify'], '%Y%m%d%H%M%S')
            file_size = int(file_info['size'])

            if file_type and not file_name.lower().endswith(file_type.lower()):
                continue

            if name_contains and name_contains.lower() not in file_name.lower():
                continue

            if date_range:
                start_date, end_date = date_range
                if file_mod_datetime < start_date or file_mod_datetime > end_date:
                    continue

            if (min_size is not None and file_size < min_size) or (max_size is not None and file_size > max_size):
                continue

            filtered_files.append((scan_ip, file_name))

        ftp.quit()

        if filtered_files:
            ftp_data.append(filtered_files)

    except Exception as e:
        logging.error(f'[search module] {scan_ip}: {str(e)}')

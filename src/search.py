# -*- coding: utf-8 -*-

"""
    This module implements the searching of FtpSiteSearchEngine.

    :author: Sam Yang (samyangcoder@gmail.com)
    :license: MIT

    :test example: 208.118.235.20
"""

from ftplib import FTP
from multiprocessing import Process, Queue
from tkinter.ttk import *
import re
import threading
import os
import logging
logging.basicConfig(level=logging.INFO)

ftp_data = {}
count = 0  # ftp 搜索计数


# 匿名登录扫描函数
def anonymous_scan(host_ip):
    logging.info('[search module]thread `%s` is running...' % threading.current_thread().name)

    global count
    count += 1

    try:
        with FTP(host_ip, timeout=10) as ftp:  # 创建 Ftp 对象
            ftp.login()  # Ftp 匿名登录
            logging.info('[search module]FTP info: (%s) FTP anonymous login succeeded!' % host_ip)
            print('Welcome message(%s):' % host_ip, ftp.getwelcome())
            ftp_data[host_ip] = ftp.nlst()
            print('\n####\n', host_ip, '\n', ftp.nlst(), '\n####\n')
            return True
    except OSError as e:
        logging.error('[search module]FTP Error: (%s) FTP anonymous login failed!' % host_ip)
        logging.info('[search module]failure info: (%s) %s' % (host_ip, 'OSError'))
        return False
    except EOFError as e:
        logging.error('[search module]FTP Error: (%s) FTP anonymous login failed!' % host_ip)
        logging.info('[search module]failure info: (%s) %s' % (host_ip, 'EOFError'))
        return False
    finally:
        logging.info('[search module]thread `%s` ended.\n' % threading.current_thread().name)


# 对用户的输入进行提取并传输参数给扫描函数
def search_ftp(q, ip_from, ip_to):
    logging.info('[search module]ipFrom is %s' % ip_from)
    logging.info('[search module]ipTo is %s' % ip_to)

    # 抽取最左侧 24 比特位地址，只进行最后八位的地址区间的扫描
    base_ip_list = re.findall('(\d+\.\d+\.\d+\.)(\d+)', ip_from)
    base_ip_str = base_ip_list[0][0]  # ip 地址的前 24 比特位，包括最后一个 `.`
    start_tail_ip_str = base_ip_list[0][1]  # ip 地址的最后 8 比特位的起始值 (即 ip_from 的最后 8 比特位)
    end_tail_ip_str = re.findall('\d+\.\d+\.\d+\.(\d+)', ip_to)[0]  # ip 地址的最后 8 比特位的终止值 (即 ip_to 的最后 8 比特位，< 256)
    logging.info('[search module](%s - %s): base_ip: %s' % (ip_from, ip_to, base_ip_str))
    logging.info('[search module](%s - %s): start_tail_ip: %s' % (ip_from, ip_to, start_tail_ip_str))
    logging.info('[search module](%s - %s): end_tail_ip: %s' % (ip_from, ip_to, end_tail_ip_str))

    # 新建线程对八位地址空间剩余 ip 进行扫描
    logging.info('[search module]thread `%s` is running...\n\n' % threading.current_thread().name)
    expected_count = int(end_tail_ip_str) - int(start_tail_ip_str) + 1
    for i in range(int(start_tail_ip_str), int(end_tail_ip_str) + 1):
        scan_ip = base_ip_str + str(i)
        t = threading.Thread(target=anonymous_scan, args=(scan_ip,), name='searchThread' + str(i))  # 新建一个线程执行搜索任务
        t.start()  # 开始执行线程
        t.join()  # 子线程调用此方法时主线程会被阻塞，直到子线程执行完毕才会继续执行主线程
        if expected_count == count:
            q.put(ftp_data)
    return True


# 新建子进程来执行多线程搜索
def search(app, ip_from, ip_to):
    logging.info('[search module]Parent process %s.' % os.getpid())
    q = Queue()
    p = Process(target=search_ftp, args=(q, ip_from, ip_to))
    logging.info('[search module]Child process will start...')
    p.start()
    p.join()
    logging.info('[search module]Child process ended.')
    print('[search module]******** { All ftp searching is done! } ********')
    ftp_data_dict = q.get(True)

    app.loading.place_forget()

    # 建立目录树
    tree = Treeview()
    tree.insert('', 0, text="Results")
    logging.info('[search module]tree width is %s' % tree.winfo_reqwidth())
    index = 0

    for (k, v) in ftp_data_dict.items():
        index += 1
        item = tree.insert('', index, k, text=k)
        for (sub_key, value) in enumerate(v):
            length = len(v)
            if sub_key == length - 1:
                tree.insert(item, 'end', value + k, text=value)  # 第三个参数之所以设置为`value + k`是因为官方文档指出`iid`必须唯一
                break
            tree.insert(item, sub_key, value + k, text=value)

    tree.place(x=300, y=150)



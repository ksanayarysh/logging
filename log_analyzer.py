#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gzip
import logging
import os
import re
from collections import namedtuple

# log_format ui_short '$remote_addr  $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)


def get_last_file():
    last_date = 0
    last_ext = ""
    last_filename = ""
    FileInfo = namedtuple('FileInfo', 'path date ext')
    log_dir = config["LOG_DIR"]
    file_mask = r"^nginx-access-ui\.(log-(\d{8})$|log-(\d{8}).gz$)"
    try:
        for file in os.listdir(log_dir):
            match = re.search(file_mask, file)
            if match:
                file_date = match.group(1).split("-")[1].split('.')
                if int(file_date[0]) > last_date:
                    last_date = int(file_date[0])
                    try:
                        last_ext = match.group(1).split('.')[1]
                    except:
                        last_ext = ''
                    last_filename = match.group(0)
    except:
        logging.error("No such directory {}".format(log_dir))

    print(last_date, last_ext, last_filename)
    return FileInfo(last_filename, last_date, last_ext)


def parse_log(file_info):
    url_time_re = r'.* \[.*\] "\w* (.*) HTTP.*(\d\.\d\d\d)'
    full_path = os.path.join(os.path.curdir, config["LOG_DIR"], file_info.path)
    log_file = open(full_path, "r") if not file_info.ext else gzip.open(full_path, "r")
    r = log_file.read()
    match = re.findall(url_time_re, r, re.MULTILINE)

    tup = [(m[0], m[1]) for m in match]
    # print(tup)
    logging.info("tuple created")
    res_table = []
    uniqie_urls = set(m[0] for m in tup)
    all_time = sum([float(m[1]) for m in tup])
    # uniqie_urls = set(m[0] for m in match)
    # all_time = sum([float(m[1]) for m in match])
    logging.info(all_time)
    logging.info(len(uniqie_urls))
    i = 0
    for u in uniqie_urls:
        i += 1
        print("Обработано {}  записей из  {}".format(i, len(uniqie_urls)))
        info = {"url": u}
        time_sum = sum([float(m[1]) for m in tup if m[0] == u])
        count = len([float(m[1]) for m in tup if m[0] == u])
        # time_sum = sum([float(m[1]) for m in match if m[0] == u])
        # count = len([float(m[1]) for m in match if m[0] == u])
        # time_avg = statistics.mean([float(m[1]) for m in match if m[0] == u])
        # time_med = statistics.median([float(m[1]) for m in match if m[0] == u])
        # time_max = max([float(m[1]) for m in match if m[0] == u])
        info['time_sum'] = time_sum
        info['count'] = count
        # info['time_avg'] = time_avg
        # info['time_med'] = time_med
        # info['time_max'] = time_max
        info['count_perc'] = (count / len(match) * 100)
        info['time_perc'] = (time_sum / all_time * 100)

        res_table.append(info)
    sorted_res = sorted(res_table, key=lambda line: line['time_sum'], reverse=True)
    for r in sorted_res:
        print(r)
    return sorted_res


def save_report(res):
    from string import Template
    with open("log/report.html", "r") as f:
        rep_text = f.read()
    s = Template(rep_text)
    l = s.safe_substitute(table_json=res)
    with open("log/report123.html", "w") as f:
        f.write(l)


def main():
    log = get_last_file()
    print(type(log))
    print(log)
    res = parse_log(log)
    save_report(res)


#     генератор для обработки логов чтобы было просто забрать нужное количество значений


if __name__ == "__main__":
    main()

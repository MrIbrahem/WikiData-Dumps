"""
from dump.claims.read_dump import read_file
python3 core8/pwb.py dump/claims/read_dump test
python3 /mnt/nfs/labstore-secondary-tools-project/himo/wd_core/dump/claims/read_dump.py test

https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

"""
import os
import json
import sys
import codecs
import bz2
import time
from datetime import datetime
from pathlib import Path
# ---
time_start = time.time()
print(f"time_start:{str(time_start)}")
# ---
# split after /dump
core_dir = str(Path(__file__)).replace('\\', '/').split("/dump/", maxsplit=1)[0]
print(f'core_dir:{core_dir}')
sys.path.append(core_dir)
print(f'sys.path.append:core_dir: {core_dir}')
# ---
from dump.memory import print_memory
va_dir = Path(__file__).parent
# ---
# from dump.claims.fix_dump import fix_props
# ---
filename = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
# ---
Dump_Dir = "/data/project/himo/dumps"
# ---
if os.path.exists(r'I:\core\dumps'):
    Dump_Dir = r'I:\core\dumps'
# ---
print(f'Dump_Dir:{Dump_Dir}')
# ---
test_limit = {1: 15000}
# ---
for arg in sys.argv:
    arg, _, value = arg.partition(':')
    if arg == "-limit":
        test_limit[1] = int(value)
# ---
cc = {1:0}
tt = {1: time.time()}
# ---
tab = {
    "delta": 0,
    "done": 0,
    "file_date": '',
    "len_all_props": 0,
    "items_0_claims": 0,
    "items_1_claims": 0,
    "items_no_P31": 0,
    "All_items": 0,
    "all_claims_2020": 0,
    "properties": {},
    "langs": {},
}


def log_dump(tab, _claims="claims"):
    # ---
    if 'nodump' in sys.argv:
        return
    # ---
    jsonname = f"{Dump_Dir}/{_claims}.json"
    # ---
    if 'test' in sys.argv:
        jsonname = f"{Dump_Dir}/{_claims}_test.json"
    # ---
    with open(jsonname, "w", encoding='utf-8') as outfile:
        json.dump(tab, outfile)
    # ---
    print("log_dump done")


def do_line(line):
    # ---
    line = line.strip("\n").strip(",")
    tab['done'] += 1
    # ---
    if 'pp' in sys.argv:
        print(line)
    # ---
    if line.startswith("{") and line.endswith("}"):
        tab['All_items'] += 1
        cc[1] += 1
        # ---
        json1 = json.loads(line)
        # ---
        claims = json1.get("claims", {})
        # ---
        if len(claims) == 0:
            tab['items_0_claims'] += 1
        else:
            # ---
            if len(claims) == 1:
                tab['items_1_claims'] += 1
            # ---
            if "P31" not in claims:
                tab['items_no_P31'] += 1
            # ---
            claims_example = {"claims": {"P31": [{"mainsnak": {"snaktype": "value", "property": "P31", "hash": "b44ad788a05b4c1b2915ce0292541c6bdb27d43a", "datavalue": {"value": {"entity-type": "item", "numeric-id": 6256, "id": "Q6256"}, "type": "wikibase-entityid"}, "datatype": "wikibase-item"}, "type": "statement", "id": "Q805$81609644-2962-427A-BE11-08BC47E34C44", "rank": "normal"}]}}
            # ---
            for p in claims.keys():
                Type = claims[p][0].get("mainsnak", {}).get("datatype", '')
                # ---
                if Type == "wikibase-item":
                    if p not in tab['properties']:
                        tab['properties'][p] = {
                            "qids": {"others": 0},
                            "lenth_of_usage": 0,
                            "len_prop_claims": 0,
                        }
                    tab['properties'][p]["lenth_of_usage"] += 1
                    tab['all_claims_2020'] += len(claims[p])
                    # ---
                    for claim in claims[p]:
                        tab['properties'][p]["len_prop_claims"] += 1
                        # ---
                        datavalue = claim.get("mainsnak", {}).get("datavalue", {})
                        # ttype = datavalue.get("type")
                        # ---
                        # print(f"ttype:{ttype}")
                        # ---
                        # if ttype == "wikibase-entityid":
                        idd = datavalue.get("value", {}).get("id")
                        # ---
                        del datavalue
                        # ---
                        if idd:
                            if idd not in tab['properties'][p]["qids"]:
                                tab['properties'][p]["qids"][idd] = 1
                            else:
                                tab['properties'][p]["qids"][idd] += 1
                        # ---
                        del idd
        # ---
        del json1
        del claims

def get_file_info(file_path):
    # Get the time of last modification
    last_modified_time = os.path.getmtime(file_path)

    return datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d')

def check_file_date(file_date):
    with codecs.open(f"{va_dir}/file_date.txt", "r", encoding='utf-8') as outfile:
        old_date = outfile.read()
    # ---
    print(f"file_date: {file_date}, old_date: {old_date}")
    # ---
    if old_date == file_date and 'test' not in sys.argv and 'test1' not in sys.argv:
        print(f"file_date: {file_date} <<lightred>> unchanged")
        sys.exit(0)

def read_lines():
    print("def read_lines():")
    # with bz2.open(filename, "r", encoding="utf-8") as f:
    with bz2.open(filename, "rt", encoding="utf-8") as f:
        # for line in f: do_line(line)
        # ---
        for line in f:
            # line = line.decode("utf-8").strip("\n").strip(",")
            do_line(line)
            # ---
            if cc[1] % 100000 == 0:
                print(cc[1], time.time() - tt[1])
                tt[1] = time.time()
                # print memory usage
                print_memory()
            # ---
            if cc[1] % 1000000 == 0:
                log_dump(tab)

def read_lines_test():
    print("def read_lines_test():")
    # with bz2.open(filename, "r", encoding="utf-8") as f:
    with bz2.open(filename, "rt", encoding="utf-8") as f:
        # for line in f: do_line(line)
        # ---
        for line in f:
            # line = line.decode("utf-8").strip("\n").strip(",")
            do_line(line)
            # ---
            if cc[1] % 100 == 0:
                print(f'cc[1]:{cc[1]}')
                print(f"done:{tab['done']}")
                # ---
                print(cc[1], time.time() - tt[1])
                tt[1] = time.time()
                # print memory usage
                print_memory()
            # ---
            if cc[1] > test_limit[1]:
                print('cc[1]>test_limit[1]')
                break

def read_file():
    # ---
    print(f"read_file: read file: {filename}")

    if not os.path.isfile(filename):
        print(f"file {filename} <<lightred>> not found")
        return {}

    tab['file_date'] = get_file_info(filename)
    print(f"file date: {tab['file_date']}")

    print(f"file {filename} found, read it:")
    # ---
    check_file_date(tab['file_date'])
    # ---
    if 'test' in sys.argv:
        read_lines_test()
    else:
        read_lines()
    # ---
    print(f"read all lines: {tab['done']}")
    # ---
    for x, xx in tab['properties'].copy().items():
        tab['properties'][x]["len_of_qids"] = len(xx["qids"])
        # tab['properties'][x]["qids"] = {k: v for k, v in sorted(xx['qids'].items(), key=lambda item: item[1], reverse=True)}
    # ---
    tab['len_all_props'] = len(tab['properties'])
    # ---
    end = time.time()
    # ---
    delta = int(end - time_start)
    tab['delta'] = f'{delta:,}'
    # ---
    print(f"read_file: done in {tab['delta']}")
    # ---
    log_dump(tab)
    # ---
    if 'test' not in sys.argv and 'nodump' not in sys.argv:
        with codecs.open(f"{va_dir}/file_date.txt", "w", encoding='utf-8') as outfile:
            outfile.write(tab['file_date'])


if __name__ == "__main__":
    read_file()

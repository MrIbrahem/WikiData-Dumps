"""
from dump.claims.read_dump import read_file
python3 wd_core/dump/claims/read_dump.py test

https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

"""
import bz2
from . import config
import codecs
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dump.memory import print_memory

# ---
time_start = time.time()
print(f"time_start:{str(time_start)}")
# ---
claims_directory = config.CLAIMS_DIRECTORY
# ---
# split after /dump
core_dir = str(Path(__file__)).replace('\\', '/').split("/dump/", maxsplit=1)[0]
print(f'core_dir:{core_dir}')
sys.path.append(core_dir)
print(f'sys.path.append:core_dir: {core_dir}')
# ---
from dump.memory import print_memory


# ---
filename = "/mnt/nfs/dumps-clouddumps1002.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.bz2"
# ---
dump_dir = "/data/project/himo/dumps"
# ---
if os.path.exists(r'I:\core\dumps'):
    dump_dir = r'I:\core\dumps'
# ---
print(f'dump_dir: {dump_dir}')
# ---
test_limit_dict = config.TEST_LIMIT_DICT
# ---
for arg in sys.argv:
    arg, _, value = arg.partition(':')
    if arg == "-limit":
        test_limit_dict[1] = int(value)
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
    jsonname = f"{dump_dir}/{_claims}.json"
    # ---
    if 'test' in sys.argv:
        jsonname = f"{dump_dir}/{_claims}_test.json"
    # ---
    with open(jsonname, "w", encoding='utf-8') as outfile:
        json.dump(tab, outfile)
    # ---
    print("log_dump done")


def get_file_info(file_path):
    # Get the time of last modification
    last_modified_time = os.path.getmtime(file_path)

    return datetime.fromtimestamp(last_modified_time).strftime('%Y-%m-%d')


def check_file_date(file_date):
    with codecs.open(str(config.CLAIMS_DIRECTORY / "file_date.txt"), "r", encoding='utf-8') as outfile:
        old_date = outfile.read()
    # ---
    print(f"file_date: {file_date}, old_date: {old_date}")
    # ---
    if old_date == file_date and 'test' not in sys.argv:
        print(f"file_date: {file_date} <<lightred>> unchanged")
        sys.exit(0)


def read_file(mode="rt"):
    print(f"read file: {filename}")

    if not os.path.isfile(filename):
        print(f"file {filename} not found")
        return {}

    start_time = time.time()
    tab['file_date'] = get_file_info(filename)
    print(f"file date: {tab['file_date']}")

    print(f"file {filename} found, read it:")
    count = 0
    # ---
    check_file_date(tab['file_date'])
    # ---

    with bz2.open(filename, mode, encoding="utf-8") as file:
        for line in file:
            line = line.decode("utf-8").strip("\n").strip(",")
            tab['done'] += 1  # Counts the number of lines processed
            # ---
            if 'pp' in sys.argv:
                print(line)
            # ---
            if line.startswith("{") and line.endswith("}"):
                tab['All_items'] += 1  # Increment the count of all processed items
                count += 1
                if 'test' in sys.argv:
                    if count % 100 == 0:
                        print(f'count:{count}')
                        print(f"done:{tab['done']}")
                        # ---
                        print(count, time.time() - start_time)
                        start_time = time.time()

                    if count > config.TEST_LIMIT_DICT[1]:
                        print('count>test_limit[1]')
                        break

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
                    for property in claims.keys():
                        datatype = claims[property][0].get("mainsnak", {}).get("datatype", '')
                        # ---
                        if datatype == "wikibase-item":
                            if property not in tab['properties']:
                                tab['properties'][property] = {
                                    "qids": {"others": 0},
                                    "lenth_of_usage": 0,
                                    "len_prop_claims": 0,
                                }
                            tab['properties'][property]["lenth_of_usage"] += 1
                            tab['all_claims_2020'] += len(claims[property])
                            # ---
                            for claim in claims[property]:
                                tab['properties'][property]["len_prop_claims"] += 1
                                # ---
                                datavalue = claim.get("mainsnak", {}).get("datavalue", {})

                                idd = datavalue.get("value", {}).get("id")
                                # ---
                                if idd:
                                    if idd not in tab['properties'][property]["qids"]:
                                        tab['properties'][property]["qids"][idd] = 1
                                    else:
                                        tab['properties'][property]["qids"][idd] += 1
                                # ---
                                del idd
                                # ---
                                del datavalue

                # ---
                del json1
                del claims
            # ---
            if (count % 1000 == 0 and count < 100000) or count % 100000 == 0:
                print(count, time.time() - start_time)
                start_time = time.time()
                # print memory usage
                print_memory()
                if count % 1000000 == 0:
                    log_dump(tab)
            # ---
    # ---
    print(f"read all lines: {tab['done']}")
    # ---
    for property_key, property_value in tab['properties'].copy().items():
        tab['properties'][property_key]["len_of_qids"] = len(property_value["qids"])
        # Sort QIDs by their count in descending order and update in the 'tab' dictionary
        # sorted_qids = sorted(property_value['qids'].items(), key=lambda item: item[1], reverse=True)
        # tab['properties'][property_key]["qids"] = dict(sorted_qids)
    # ---
    tab['len_all_props'] = len(tab['properties'])  # Calculate the total number of unique properties processed
    # ---
    end = time.time()
    # ---
    delta = int(end - time_start)
    tab['delta'] = f'{delta:,}'
    # ---
    log_dump(tab)
    # ---
    with codecs.open(str(config.CLAIMS_DIRECTORY / "file_date.txt"), "w", encoding='utf-8') as outfile:
        outfile.write(tab['file_date'])
    # ---


if __name__ == "__main__":
    read_file()

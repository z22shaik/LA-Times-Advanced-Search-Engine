import sys
import os
from pathlib import Path
import gzip
from xml.sax.handler import DTDHandler
import pickle
import pdb
import json
import re
from datetime import datetime
substring_1 = "docno"
substring_2 = "id"
doc_no = ""

# Retrieved from
# https://stackoverflow.com/questions/2194163/python-empty-argument
if len(sys.argv) == 1 or len(sys.argv) == 2 or len(sys.argv) == 3 or len(sys.argv) > 4:
    # Retrieved from
    # https://www.edureka.co/community/54600/how-to-terminate-a-python-script#:~:text=In%20particular%2C%20sys.,Hope%20it%20works!!
    sys.exit("The purpose of this program is to provide a file path for a document, with its associated document number or id in order to access it. "
             + "\nTo retrieve a document, please use the following three arguments: \n1. The file path for the document, 2. Specify whether you are searching through"
             + " docno or id, and 3. Provide the associated docno or id.")

storage_path = sys.argv[1]
storage_path_new = Path(storage_path)
storage_path_metadata = storage_path_new / "Metadata"
given_type = sys.argv[2]
given_key = sys.argv[3]


# Retrieved from
# https://stackoverflow.com/questions/40287003/reformat-a-date-string-with-hyphens
def parse(date):
    return "{}-{}-{}".format(date[:2], date[2:4], date[4:6])


# Lines 30 to 38 are copied from:
# https://stackoverflow.com/questions/66272727/remove-comments-and-add-commas-between-json-objects
f = open(storage_path_metadata, "r")
a = f.read()
# remove all occurrence single-line comments (//COMMENT\n ) from string
a = re.sub(re.compile("//.*?\n"), "", a)
a = a.replace("\n", "")                   # remove all breakline from string
a = a.replace("}{", "},{")                # {x:y} {h:j} => {x:y},{h:j}
a = "[" + a + "]"
load = json.loads(a)
#print(json.dumps(load, indent=3))

# with open(storage_path_metadata) as file:
#     loaded = json.load(file)
#     print(loaded)

# metadata_list = []
# for line in open(storage_path_metadata, "r"):
#     metadata_list.append(json.loads(line))
if substring_1 in given_type:
    #date_value = ""
    doc_no = given_key
    #     # Retrieved from:
    #     # https://stackoverflow.com/questions/40827356/find-a-value-in-json-using-python
    # for i in load:
    #     if load[i]['docno'] == given_key:
    #         print(load[i]['docno'])
    #         print(load[i]['internal id'])
    #         print(load[i]['date'])
    #         print(load[i]['headline'])
    #         break
    for value in load:
        if value['docno'] == given_key:
            new_date = parse(value['date'])
            # Retrieved from
            # https://pynative.com/python-datetime-format-strftime/#h-example-convert-datetime-to-string-format
            new_new_date = datetime.strptime(new_date, '%d-%m-%y').date()
            # print(new_new_date)
            date_text = "\ndate: " + new_new_date.strftime("%B %-d, %Y")
            #print("dd-mm-yy Format:", new_date.strftime("%d-%m-%y"))
           # print("dd-MonthName-yyyy:",
            #   WOO=new_date.strftime("%-d %B, %Y"))
            print("docno: " + value['docno'], "\ninternal id: " +
                  value['internal id'], date_text, "\nheadline: " + value['headline'])
            date_value = value['date']
    date_value_check = "date_value" in locals()
    if date_value_check == False:
        sys.exit("There is no docno that exists given your input.")

if substring_2 in given_type:
    #     # Retrieved from:
    #     # https://stackoverflow.com/questions/40827356/find-a-value-in-json-using-python
    # for i in load:
    #     if load[i]['docno'] == given_key:
    #         print(load[i]['docno'])
    #         print(load[i]['internal id'])
    #         print(load[i]['date'])
    #         print(load[i]['headline'])
    #         break

    # Retrieved from:
    # https://stackoverflow.com/questions/54431719/python-iterate-through-json-list-to-match-specific-key-value-pair
    for value in load:
        if value['internal id'] == given_key:
            new_date = parse(value['date'])
            new_new_date = datetime.strptime(new_date, '%d-%m-%y').date()
            # print(new_new_date)
            date_text = "\ndate: " + new_new_date.strftime("%B %-d, %Y")
            #print("dd-mm-yy Format:", new_date.strftime("%d-%m-%y"))
           # print("dd-MonthName-yyyy:",
            #   WOO=new_date.strftime("%-d %B, %Y"))
            print("docno: " + value['docno'], "\ninternal id: " +
                  value['internal id'], date_text, "\nheadline: " + value['headline'])
            doc_no = value['docno']
            date_value = value['date']
    date_value_check = "date_value" in locals()
    if date_value_check == False:
        sys.exit("There is no internal id that exists given your input.")

if not substring_2 in given_type and not substring_1 in given_type:
    sys.exit("Please enter either a docno or id as the input type.")

storage_path_doc = storage_path_new / date_value / doc_no
print("raw document:")
with open(storage_path_doc) as f:  # The with keyword automatically closes the file when you are done
    print(f.read())

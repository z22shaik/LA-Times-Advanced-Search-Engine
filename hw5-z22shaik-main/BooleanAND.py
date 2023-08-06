
from lib2to3.pgen2 import token
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
from collections import defaultdict

# Retrieved from
# https://stackoverflow.com/questions/2194163/python-empty-argument
if len(sys.argv) == 1 or len(sys.argv) == 2 or len(sys.argv) == 3 or len(sys.argv) > 4:
    # Retrieved from
    # https://www.edureka.co/community/54600/how-to-terminate-a-python-script#:~:text=In%20particular%2C%20sys.,Hope%20it%20works!!
    sys.exit("The purpose of this program is to provide a file path for an index, queries file, and a name for an output file. "
             + "\nThe program then outputs the result for all of the provided queries.")

index_path = sys.argv[1]
index_path_new = Path(index_path)
queries_path = sys.argv[2]
queries_path_new = Path(queries_path)
output_path = sys.argv[3]
output_path_new = Path(output_path)

storage_path_lexicon = index_path_new / "Lexicon"
storage_path_index = index_path_new / "InvertedIndex"
storage_path_metadata = index_path_new / "Metadata"

if os.path.exists(output_path_new):
    sys.exit("Output file already exists!")


# Lines 30 to 38 are copied from:
# https://stackoverflow.com/questions/66272727/remove-comments-and-add-commas-between-json-objects
f1 = open(storage_path_index, "r")
a1 = f1.read()
# remove all occurrence single-line comments (//COMMENT\n ) from string
a1 = re.sub(re.compile("//.*?\n"), "", a1)
a1 = a1.replace("\n", "")                   # remove all breakline from string
a1 = a1.replace("}{", "},{")                # {x:y} {h:j} => {x:y},{h:j}
a1 = "[" + a1 + "]"
loaded_inverted_index = json.loads(a1)
loaded_inverted_index = loaded_inverted_index[0]
# print(loaded_inverted_index)


f = open(storage_path_lexicon, "r")
a = f.read()
# remove all occurrence single-line comments (//COMMENT\n ) from string
a = re.sub(re.compile("//.*?\n"), "", a)
a = a.replace("\n", "")                   # remove all breakline from string
a = a.replace("}{", "},{")                # {x:y} {h:j} => {x:y},{h:j}
a = "[" + a + "]"
loaded_lexicon = json.loads(a)
loaded_lexicon = loaded_lexicon[0]
# print(loaded_lexicon)

f2 = open(storage_path_metadata, "r")
a2 = f2.read()
# remove all occurrence single-line comments (//COMMENT\n ) from string
a2 = re.sub(re.compile("//.*?\n"), "", a2)
a2 = a2.replace("\n", "")                   # remove all breakline from string
a2 = a2.replace("}{", "},{")                # {x:y} {h:j} => {x:y},{h:j}
a2 = "[" + a2 + "]"
loaded_metadata = json.loads(a2)


def tokenize(s: str):
    s = s.lower()
    tokens = []
    start = 0
    for curr in range(len(s)):
        if not s[curr].isalnum():
            if curr != start:
                tokens.append(s[start:curr])
            start = curr+1
        if s[curr].isalnum() and curr == len(s)-1:
            tokens.append(s[start:curr+1])
    return tokens


def convert_to_ids(tokens: list, lexicon: dict):
    token_ids = []
    # print(lexicon)
    for token in tokens:
        # print(token)
        if token not in lexicon:
            lexicon[token] = len(lexicon)
        token_ids.append(lexicon[token])
    # print(token_ids)
    return token_ids


def booleanAND(query: str, inverted_index: dict, lexicon: dict):
    doc_counts = defaultdict(int)
    num_token_appears = defaultdict(int)
    query_tokens = tokenize(query)
    # print(query_tokens)
    # for t in query_tokens:
    #     print(lexicon[t])
    query_token_ids = convert_to_ids(query_tokens, lexicon)
    # print(query_token_ids)
    for token_id in query_token_ids:
        # print(token_id)
        #input = str(lexicon[0][token_id])
        if str(token_id) in inverted_index:
            postings = inverted_index[str(token_id)]
            # print(postings)
            for i in range(len(postings)):
                if i % 2 == 0:
                    doc_counts[postings[i]] += 1
                else:
                    num_token_appears[postings[i-1]] += postings[i]
                    # number of times token appears in a doc is equal to the next value of postings
                    # print(postings)
                    # for doc_id in postings:
                    #     doc_counts[doc_id] += 1
        # print(doc_counts)
    result = []
    for doc_id in doc_counts:
        if doc_counts[doc_id] == len(query_token_ids):
            result.append(doc_id)
    # print(result)
    result_num_token = defaultdict(int)
    for item in result:
        result_num_token[item] = num_token_appears[item]
    return [result, result_num_token]


even_or_odd = 0
with open(queries_path_new) as f:
    for new_line in f.readlines():
        if even_or_odd % 2 == 1:
            # print(loaded_lexicon[0])
            # print(loaded_inverted_index[0]["0"])
            count_list = []
            # pass result, topic id
            total_result = booleanAND(
                new_line, loaded_inverted_index, loaded_lexicon)
            result = total_result[0]
            # print(result)
            # print(len(result))
            num_token_appears = total_result[1]
            # print(num_token_appears)
            with open(str(output_path_new), 'a') as f2:
                for item in result:  # for each doc id in result
                    for key, value in num_token_appears.items():  # for each key, value pair in num_token
                        # if the doc id in results = the current doc id
                        if key == item:  # if key to num_tokens equals current doc id in results
                            # Add the count for total of all query tokens for the doc
                            count_list.append(int(value))
                    # sort list descending
                count_list.sort(reverse=True)
                # print(count_list)
                rank = 1
                # print(topic_number)
                # iterate through rank list
                # print(count_list)
                # print(num_token_appears)
                for count in count_list:
                    for key, value in num_token_appears.items():
                        if value == count:
                            doc_id = key
                           # print(doc_id)
                            break
                            # WHAT TO DO FOR TWO MATCHING COUMTS
                    del num_token_appears[doc_id]
                    # print(num_token_appears)
                    for value in loaded_metadata:
                        if value['internal id'] == str(doc_id):
                            # print(doc_id)
                            doc_no = value['docno']
                            # print(doc_no)
                    f2.write(topic_number)
                    f2.write(" ")
                    f2.write(" Q0 ")
                    # print(doc_no)
                    f2.write(str(doc_no))
                    f2.write(" ")
                    f2.write(str(rank))
                    f2.write(" ")
                    f2.write(str(len(count_list)-rank))
                    f2.write(" ")
                    f2.write("z22shaikAND\n")
                    rank += 1
                    # find docs associated using num_token_appears dictionary, finding key using value
                    # print(line)
                    # print(result)
        else:
            topic_number = new_line.strip()
        even_or_odd = even_or_odd + 1

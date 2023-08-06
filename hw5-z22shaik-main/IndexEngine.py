# Take two arguments from command line
import sys
import os
from pathlib import Path
import gzip
from xml.sax.handler import DTDHandler
import pickle
import pdb
import json
import time
from nltk.stem import PorterStemmer

p = PorterStemmer()
porter = True

# Retrieved from
# https://stackoverflow.com/questions/2194163/python-empty-argument
if len(sys.argv) == 1 or len(sys.argv) == 2 or len(sys.argv) > 3:
    # Retrieved from
    # https://www.edureka.co/community/54600/how-to-terminate-a-python-script#:~:text=In%20particular%2C%20sys.,Hope%20it%20works!!
    sys.exit("Please provide two arguments: 1. A file path to the latimes.gz file and 2. A path to a directory where the documents and metadata will be stored")

la_path = sys.argv[1]
la_path_new = Path(la_path)
storage_path = sys.argv[2]
storage_path_new = Path(storage_path)


# Retrieved from
# https://stackoverflow.com/questions/14360389/getting-file-path-from-command-line-argument-in-python
if not os.path.exists(la_path_new):
    # print(os.path.basename(la_path))
    # print(os.path.basename(storage_path))
    sys.exit("You have provided the wrong file path to access the latimes.gz file")

if os.path.exists(storage_path_new):
    sys.exit("Directory already exists!")
else:
    # Retrieved from
    # https://www.adamsmith.haus/python/answers/how-to-create-files-and-directories-in-python
    os.mkdir(storage_path_new)
    storage_path_metadata = storage_path_new / "Metadata"
    os.makedirs(os.path.dirname(str(storage_path_metadata)), exist_ok=True)
    storage_path_len = storage_path_new / "Doclengths"
    os.makedirs(os.path.dirname(str(storage_path_len)), exist_ok=True)
    storage_path_inverted = storage_path_new / "InvertedIndex"
    os.makedirs(os.path.dirname(str(storage_path_inverted)), exist_ok=True)
    storage_path_lexicon = storage_path_new / "Lexicon"
    os.makedirs(os.path.dirname(str(storage_path_lexicon)), exist_ok=True)
    storage_path_len2 = storage_path_new / "DoclengthsID"
    os.makedirs(os.path.dirname(str(storage_path_len2)), exist_ok=True)
# Method to extract metadata


def meta_extract_write(doc_no, doc_id, doc_date, headline_string):
    # if not storage_path_metadata.is_file():
    # with open(str(storage_path_metadata), "w") as f:
    # f.write("\n docno: " + doc_no)
    # f.write("\n internal id: " + doc_id)
    # HAVE TO CONVERT THIS TO WRITTEN DATE
    # f.write("\n date: " + doc_date)
    # with open('headline.pkl', 'rb') as fe:
    #  headline_from_storage = pickle.load(fe)
    # f.write("\n".join(headline_from_storage))

    headline_string_new = headline_string.strip()
    headline_string_new_new = headline_string_new.replace("<P>", "").replace(
        "<\P>", "").replace("<HEADLINE>", "").replace("<\HEADLINE>", "").replace("<P>\n", "").replace("<\P>\n", "").replace("<HEADLINE>\n", "").replace("<\HEADLINE>\n", "").replace("\n<P>", "").replace("\n<\P>", "").replace("\n<HEADLINE>", "").replace("\n<\HEADLINE>", "").replace("\n", "").replace("; </P>", "; ").replace(" </P></HEADLINE>", "")
    headline_string_new_new_new = headline_string_new_new.strip()
    # f.write("\n headline: " + headline_string_new_new_new)
    dict_data = {
        "docno": doc_no,
        "internal id": doc_id,
        "date": doc_date,
        "headline": headline_string_new_new_new,
        # "doc len": token_len
    }
    meta_json_object = json.dumps(dict_data, indent=3)

    # dict_data2 = {
    #     doc_no: token_len
    # }

    # if os.path.exists("metadata.json"):
    #     with open(meta_file_name, "r") as file:
    #         loaded = json.loads(file.read())
    #     loaded.append(dict_data)
    # else:
    #     loaded = [dict_data]
    #     # 3. Write json file
    with open(storage_path_metadata, "a") as file:
        file.write(meta_json_object)

    # with open(storage_path_len, 'ab+') as fp:
    #     pickle.dump(dict_data2, fp)

    # else:
    # with open(str(storage_path_metadata), "a") as f:
    # f.write("\n docno: " + doc_no)
    # f.write("\n internal id: " + doc_id)
    # HAVE TO CONVERT THIS TO WRITTEN DATE
    # f.write("\n date: " + doc_date)
    # with open('headline.pkl', 'rb') as fe:
    # headline_from_storage = pickle.load(fe)
    # f.write("\n".join(headline_from_storage))
    # headline_string_new = headline_string.strip()
    # headline_string_new_new = headline_string_new.replace("<P>", "").replace(
    #  "<\P>", "").replace("<HEADLINE>", "").replace("<\HEADLINE>", "").replace("<P>\n", "").replace("<\P>\n", "").replace("<HEADLINE>\n", "").replace("<\HEADLINE>\n", "").replace("\n<P>", "").replace("\n<\P>", "").replace("\n<HEADLINE>", "").replace("\n<\HEADLINE>", "").replace("\n", "").replace("; </P>", "; ").replace(" </P></HEADLINE>", "")
    # headline_string_new_new_new = headline_string_new_new.strip()
    # f.write("\n headline: " + headline_string_new_new_new)


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


def convert_to_ids(tokens, lexicon):
    token_ids = []
    for token in tokens:
        if porter == True:
            # print(token)
            token = p.stem(token)
            # print(token)
        if token not in lexicon:
            lexicon[token] = len(lexicon)
        token_ids.append(lexicon[token])
    return token_ids


def count_words(token_ids):
    word_counts = {}
    for id in token_ids:
        if id in word_counts:
            word_counts[id] += 1
        else:
            word_counts[id] = 1
    return word_counts


def add_to_postings(word_counts: dict, doc_id: int, inverted_index: dict):
    for id in word_counts:
        count = word_counts[id]
        if id in inverted_index:
            postings = inverted_index[id]
            postings.append(doc_id)
            postings.append(count)
            inverted_index[id] = postings
        else:
            postings = []
            postings.append(doc_id)
            postings.append(count)
            inverted_index[id] = postings


# Retrieved from
# https://stackoverflow.com/questions/12902540/read-from-a-gzip-file-in-python
# all_docs = gzip.open(la_path, 'rt')
prev_date = 'initial'
# two_lines_back = ''
# prev_line = ''
graphic_section = False
text_section = False
headline_section = False
headline_list = []
lexicon = {}
inverted_index = {}
doc_lens = {}
doc_lens_from_id = {}
with gzip.open(la_path, 'rt') as big_doc:
    for line in big_doc:
        # print('got line', line)
        substring = "<DOC>"
        substring_2 = "<DOCNO>"
        substring_3 = "<DOCID>"
        substring_4 = "<HEADLINE>"
        substring_5 = "</DOC>"
        substring_6 = "<P>"
        substring_7 = "</HEADLINE>"
        substring_8 = "<TEXT>"
        substring_9 = "</TEXT>"
        substring_10 = "<GRAPHIC>"
        substring_11 = "</GRAPHIC>"
        if substring in line:
            doc = []
            doc_2 = []
            # print('got line', line)
        doc.append(line)
        if substring_2 in line:
            # Retrieved from
            # https://bobbyhadz.com/blog/python-remove-first-and-last-word-from-string#:~:text=To%20remove%20the%20first%20and,words%20of%20the%20original%20string.
            doc_no = line[line.index(' ') + 1:line.rindex(' ')]
            doc_date = doc_no[2:8]
            # print(doc_date)

        if substring_3 in line:
            doc_id = line[line.index(' ') + 1:line.rindex(' ')]

        if substring_4 in line:
            headline_section = True
        # substring_4 == two_lines_back.strip() and substring_6 == prev_line.strip():
        # headline = line
        # else:
        # headline = "\n" + two_lines_back + "\n" + prev_line

        if substring_8 in line:
            text_section = True

        if text_section == True and "<" not in line:
            doc_2.append(line)

        if substring_9 in line:
            text_section = False

        if substring_10 in line:
            graphic_section = True

        if graphic_section == True and "<" not in line:
            doc_2.append(line)

        if substring_11 in line:
            graphic_section = False

        if headline_section == True:
            headline_list.append(line)

        if headline_section == True and "<" not in line:
            doc_2.append(line)

        if substring_7 in line:
            # pdb.set_trace()
            headline_section = False

        if substring_5 in line:
            # Retrieved from
            # https://pynative.com/python-write-list-to-file/
            if prev_date == doc_date:
                storage_path_new_append = storage_path_new / \
                    prev_date/doc_no
                # os.makedirs(storage_path_new_append)
                # Retrieved from
                # https://stackoverflow.com/questions/12517451/automatically-creating-directories-with-file-output
                os.makedirs(os.path.dirname(
                    str(storage_path_new_append)), exist_ok=True)
                with open(str(storage_path_new_append), "w") as f:
                    f.write('\n'.join(doc))
                # with open("r"+str(storage_path_new_append), 'w') as txt_write:
                    # txt_write.write('\n'.join(doc))
                # for list_item in doc:
                # storage_path_new_append.write_text(list_item)
                # storage_path_new_append.write_text('\n')
            elif prev_date != doc_date:
                storage_path_new_append = storage_path_new / \
                    doc_date / doc_no
                # os.makedirs(storage_path_new_append)
                os.makedirs(os.path.dirname(
                    str(storage_path_new_append)), exist_ok=True)
                with open(str(storage_path_new_append), "w") as f:
                    f.write('\n'.join(doc))
                # with open("r"+str(storage_path_new_append), 'w') as txt_write:
                    # txt_write.write('\n'.join(doc))
                # for list_item in doc:
                # storage_path_new_append.write_text(list_item)
                # storage_path_new_append.write_text('\n')
            prev_date = doc_date
            # Create inverted index
            tokens = tokenize('\n'.join(doc_2))
            print(tokens)
            token_len = len(tokens)
            # print(tokens)
            token_ids = convert_to_ids(tokens, lexicon)
            # print(token_ids)
            word_counts = count_words(token_ids)
            add_to_postings(word_counts, int(doc_id), inverted_index)
            # Completed inverted index

            headline_string = "".join(headline_list)
            meta_extract_write(doc_no, doc_id, doc_date,
                               headline_string)
            doc_lens[doc_no] = token_len
            doc_lens_from_id[doc_id] = token_len
            headline_list = []
        # two_lines_back = prev_line
        # prev_line = line
# print(inverted_index)
meta_invert_object = json.dumps(inverted_index, indent=3)
with open(storage_path_inverted, "w") as file1:
    file1.write(meta_invert_object)

meta_lexicon_object = json.dumps(lexicon, indent=3)
with open(storage_path_lexicon, "w") as file2:
    file2.write(meta_lexicon_object)

meta_len_object = json.dumps(doc_lens, indent=3)
with open(storage_path_len, 'w') as fp:
    fp.write(meta_len_object)

meta_len2_object = json.dumps(doc_lens_from_id, indent=3)
with open(storage_path_len2, 'w') as fp:
    fp.write(meta_len2_object)

# a_file = open(storage_path_inverted, "wb")
# pickle.dump(inverted_index, a_file)
# a_file.close()

# b_file = open(storage_path_lexicon, "wb")
# pickle.dump(lexicon, b_file)
# b_file.close()

# a1_file = open(storage_path_inverted, "rb")
# output1 = pickle.load(a1_file)
# print(output1)
# a1_file.close()

# # b1_file = open(storage_path_lexicon, "rb")
# # output2 = pickle.load(b1_file)
# # print(output2)

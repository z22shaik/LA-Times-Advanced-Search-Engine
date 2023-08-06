
import argparse
from parsers import QrelsParser, ResultsParser
import sys
import math
import re
import json
import pickle
import csv
from statistics import mean
# Author: Nimesh Ghelani based on code by Mark D. Smucker

parser = argparse.ArgumentParser(description='todo: insert description')
parser.add_argument('--qrel', required=True, help='Path to qrel')
parser.add_argument('--results', required=True,
                    help='Path to file containing results')
# parser.add_argument('--max-results', type=int, required=True, help='')

# This code doesn't do much other than sort of show how the
# various classes can be used.


def main():
   # Lines 30 to 38 are copied from:
    # https://stackoverflow.com/questions/66272727/remove-comments-and-add-commas-between-json-objects
    f1 = open("/Users/zuhayrshaikh/MSCI541HW3/hw3-z22shaik/Doclengths", "r")
    a1 = f1.read()
    # remove all occurrence single-line comments (//COMMENT\n ) from string
    a1 = re.sub(re.compile("//.*?\n"), "", a1)
    # remove all breakline from string
    a1 = a1.replace("\n", "")
    a1 = a1.replace("}{", "},{")                # {x:y} {h:j} => {x:y},{h:j}
    a1 = "[" + a1 + "]"
    loaded_doc_lens = json.loads(a1)
    loaded_doc_lens = loaded_doc_lens[0]
    # print(loaded_doc_lens['LA123190-0134'])

    # Design taken from: https://stackoverflow.com/questions/12761991/how-to-use-append-with-pickle-in-python
    # file_to_read = open(
    #     "/Users/zuhayrshaikh/MSCI541HW3/hw3-z22shaik/Doclengths", 'rb')
    # objs = []
    # while 1:
    #     try:
    #         objs.append(pickle.load(file_to_read))
    #     except EOFError:
    #         break
    #     print(objs[1]['LA123090-0186'])
    # with open("/Users/zuhayrshaikh/MSCI541HW3/hw3-z22shaik/Doclengths", 'rb') as handle:
    #     doc_lens = pickle.load(handle)
    # print(doc_lens['LA123090-0186'])
    cli = parser.parse_args()
    qrel = QrelsParser(cli.qrel).parse()
    ouput_csv_name = "hw5_bert_stats.csv"
    overall_stats_output = " hw5-metrics-z22shaik.csv"
    # print (qrel)
    try:
        results = ResultsParser(cli.results).parse()
    except ValueError:
        with open(ouput_csv_name, 'w') as ofile:
            writer = csv.writer(ofile, delimiter=',')
            writer.writerow(['ID', 'average_precisions',
                            'p_10_precisions', 'ndcg_10', 'ndcg_1000', 'tbg'])
            writer.writerow(['bad format', 'bad format',
                            'bad format', 'bad format', 'bad format', 'bad format'])
        with open(overall_stats_output, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            writer = csv.writer(write_obj, delimiter=',')
            # Add contents of list as last row in the csv file
            writer.writerow(['bad format', 'bad format',
                            'bad format', 'bad format', 'bad format'])
        sys.exit("Bad results format")
    # max_results = cli.max_results

    query_ids = sorted(qrel.get_query_ids())
    # print(*query_ids)
    average_precisions = {}
    p_10_precisions = {}
    ndcg_10 = {}
    ndcg_1000 = {}
    tbg = {}
    for query_id in query_ids:
        qrel_gain_list = QrelsParser(cli.qrel).sorted_gain_list(str(query_id))
        # print(qrel_gain_list)
        # new_qrel_gain_list = qrel_gain_list.sort(reverse=True)
        qrel_gain_list.sort(reverse=True)
        gain_count = 0
        idcg_10_sum = 0
        idcg_1000_sum = 0
        dcg_10_sum = 0
        dcg_1000_sum = 0
        relevant_no_collection = 0
        tbg_sum = 0
        tk_sum = 0
        for gain in qrel_gain_list:
            if gain > 0:
                relevant_no_collection += 1
            gain_count += 1
            if gain_count <= 10:
                idcg_10_sum += ((gain) / (math.log2(gain_count + 1)))
            if gain_count <= 1000:
                idcg_1000_sum += ((gain) / (math.log2(gain_count + 1)))
        # idcg_10[query_id] = idcg_10_sum
        # print(idcg_10[query_id])
        # idcg_1000[query_id] = idcg_1000_sum
        # print(idcg_1000[query_id])
        relevant_count = 0
        query_result_no = 0
        precision_sum = 0
        try:
            query_result = sorted(results[1].get_result(query_id))
        except TypeError:
            continue
        # print(*query_result)
        # print(query_id)
        if query_result is None:
            sys.stderr.write(
                query_id+' has no results, but it exists in the qrels.\n')
            continue

        for result in query_result:
            query_result_no += 1
            # print(result.doc_id)
            # for value in load:
            #     # print(value)
            #     if value['docno'] == str(result.doc_id):
            #         doc_len = value['doc len']
            #         break
            try:
                doc_len = loaded_doc_lens[str(result.doc_id)]
            except KeyError:
                doc_len = 0

            if query_result_no > 1000:
                relevance = 0
                relevant_count += int(relevance)
                precision_sum += float((relevant_count /
                                       query_result_no)*float(relevance))
                tk_sum += 4.4 + (0.018 * float(doc_len) + 7.8) + 0.39
                tbg_sum += float(relevance) * 0.4928 * \
                    math.exp(-1.0 * tk_sum * (math.log(2))/(224))

            else:
                relevance = qrel.get_relevance(query_id, result.doc_id)
                if doc_len == 0:
                    relevance = 0
                if query_result_no <= 10:
                    dcg_10_sum += ((int(relevance)) /
                                   (math.log2(query_result_no + 1)))
                if query_result_no <= 1000:
                    dcg_1000_sum += ((int(relevance)) /
                                     (math.log2(query_result_no + 1)))
                relevant_count += int(relevance)
                precision_sum += float((relevant_count /
                                       query_result_no)*float(relevance))
                if relevance > 0 and doc_len != 0:
                    tk_sum += 4.4 + (0.018 * float(doc_len) + 7.8) * 0.64
                    tbg_sum += float(relevance) * 0.4928 * \
                        math.exp(-1.0 * tk_sum * (math.log(2))/(224))
                elif relevance == 0 and doc_len != 0:
                    tk_sum += 4.4 + (0.018 * float(doc_len) + 7.8) * 0.39
                    tbg_sum += float(relevance) * 0.4928 * \
                        math.exp(-1.0 * tk_sum * (math.log(2))/(224))
                if query_result_no == 10 and doc_len != 0:
                   # p_10_query = float(
                    # relevant_count/(query_result_no))
                    p_10_query = float(
                        relevant_count/(10))
        # precision_for_query = float(relevant_count/query_result_no)
        # precision_for_query = float(relevant_count/relevant_no_collection)
        precision_for_query = float(precision_sum)/relevant_no_collection
        average_precisions[query_id] = precision_for_query
        p_10_precisions[query_id] = p_10_query
        ndcg_10[query_id] = float(dcg_10_sum/idcg_10_sum)
        tbg[query_id] = tbg_sum
        # print(ndcg_10[query_id])
        ndcg_1000[query_id] = float(dcg_1000_sum/idcg_1000_sum)
        # print(ndcg_1000[query_id])
    # print(average_precisions)
    # print(p_10_precisions)
    print(tbg)

    # code for lines 157-165 referenced from https://stackoverflow.com/questions/22273970/writing-multiple-dictionaries-to-csv-file
    dicts = average_precisions, p_10_precisions, ndcg_10, ndcg_1000, tbg

    with open(ouput_csv_name, 'w') as ofile:
        writer = csv.writer(ofile, delimiter=',')
        writer.writerow(['ID', 'average_precisions',
                        'p_10_precisions', 'ndcg_10', 'ndcg_1000', 'tbg'])
        for key in average_precisions:
            writer.writerow([key] + [d[key] for d in dicts])

    mean_average_precision = mean(
        average_precisions[k] for k in average_precisions)
    mean_p_10 = mean(
        p_10_precisions[k] for k in p_10_precisions)
    mean_ndcg_10 = mean(
        ndcg_10[k] for k in ndcg_10)
    mean_ndcg_1000 = mean(
        ndcg_1000[k] for k in ndcg_1000)
    mean_tbg = mean(
        tbg[k] for k in tbg)

    row_values = [mean_average_precision, mean_p_10,
                  mean_ndcg_10, mean_ndcg_1000, mean_tbg]
    with open(overall_stats_output, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        writer = csv.writer(write_obj, delimiter=',')
        # Add contents of list as last row in the csv file
        writer.writerow(row_values)


if __name__ == '__main__':
    main()

#go through list of tags
#if it contains no characters other than _, remove it
#Remove all tabs

import json
import glob
import re
import pandas as pd
from textblob import TextBlob #  , tokenizers.SentenceTokenizer
import csv
import random


obviousCount = 0
notCount = 0

train_file = open("train.tsv", "w+", newline='\n')
dev_file = open("dev.tsv", "w+", newline='\n')
test_file = open("test.tsv", "w+", newline='\n')

train_writer = csv.writer(train_file, delimiter='\t')
dev_writer = csv.writer(dev_file, delimiter='\t')
test_writer = csv.writer(test_file, delimiter='\t')

train_writer.writerow(["sentence", "label"])
dev_writer.writerow(["sentence", "label"])
test_writer.writerow(["sentence", "label"])

office_actions = pd.read_csv('./data/office_actions.csv',
    index_col='app_id',
    usecols=['app_id', 'rejection_102', 'rejection_103'],
    dtype={'app_id':int, 'rejection_102': int, 'rejection_103': int},
    nrows=200000)

filenames = glob.glob("../../Documents/School/CloudML/Project3/patent-classification/json_files_1/*.json")
for filename in filenames:

    num = random.random()
    if num < 0.7:
        write_file = train_file
        writer = train_writer
    elif num >= 0.7 and num <= 0.84:
        write_file = dev_file
        writer = dev_writer
    else:
        write_file = test_file
        writer = test_writer

    try:
        app_id = int(filename.replace("oa_", "").replace(".json", "").replace("(1)", "").replace("../../Documents/School/CloudML/Project3/patent-classification/json_files_1\\",""))
    except ValueError:
        print("WARNING: app_id ValueError")
        continue

    try:
        row  = office_actions.loc[app_id]
    except KeyError:
        print("WARNING: app_id KeyError")
        continue

    try:
        n = int(row.rejection_102)
        o = int(row.rejection_103)
    except TypeError:
        n = int(row.rejection_102.iloc[0])
        o = int(row.rejection_103.iloc[0])
    label = str(o)

    if obviousCount >= notCount and o == 1:
        continue
    obviousCount += o
    notCount += not(o)


    try:
        json_file = open(filename, 'r')
    except FileNotFoundError:
        print("File Not Found")
        continue

    try:
        parsed_json = json.load(json_file)
        json_file.close()
    except UnicodeDecodeError:
        print("WARNING: UnicodeDecodeError")
        continue
    except json.decoder.JSONDecodeError:
        print("WARNING: JSONDecodeError")
        continue

    # Skip any files not in the appropriate IPC class
    try:
        found_A61 = False
        for s in parsed_json[0]['ipc_classes']:
            if (s.find("A61") != -1):
                found_A61 = True
        if not found_A61:
            continue
    except:
        print("WARNING: file {} is empty!\n".format(app_id))
        continue

    # Read in data from json file if it exists
    try:
        abstract = parsed_json[0]['abstract_full']
        claims = parsed_json[0]['claims_full']
    except IndexError:
        print("WARNING: file {} is empty!\n".format(app_id))
        continue
    except KeyError:
        print("WARNING: file {} is empty!\n".format(app_id))
        continue


    blob = TextBlob(claims)
    for sentence in blob.sentences:
        sentence = str(sentence).replace("\t", " ").replace("\n", " ")
        if not re.search('[a-zA-Z]', sentence):
            continue

        try:
            writer.writerow([sentence, label])
            print(label)
        except:
            print("error")
            continue


print('{}% are obvious'.format(obviousCount*100/(obviousCount+notCount)))
train.close()
dev.close()
test.close()

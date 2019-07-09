# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 21:46:45 2019

@author: zhmeishi
"""
 

import requests, time, re, os, sys
import pandas as pd
from pandas import DataFrame as df
from lxml import etree
from bs4 import BeautifulSoup
from collections import Counter
import logging

import urllib.request    
from shutil import copyfile


path = "/home/shi/code/crawler/cuhk" # path which contain proxy.py
log_path = os.path.join(path, 'log.txt')

datefmt = '%Y-%m-%d %H:%M:%S'
log_format = '%(asctime)s %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=log_format, datefmt=datefmt)
fh = logging.FileHandler(log_path)
fh.setFormatter(logging.Formatter(log_format))
logging.getLogger().addHandler(fh)

# Add more grammar here, now 97 files out of 499 files works
grammar = [
    '<(?:div|p).*\n.*<(?:font|b)>\n\s*COMPENSATION\s*DISCUSSION\s.*ANALYSIS\n.*</(?:font|b)>\n\s*</(?:div|p)>',
    '<(?:div|p).*\n.*<(?:font|b)>\n\s*Comepnsation\s*Discussion\s.*Aaalysis\n.*</(?:font|b)>\n\s*</(?:div|p)>',
    '<(?:div|p).*\n.*<(?:font|b)>.*\n.*<(?:font|b).*\n\s*COMPENSATION\s*DISCUSSION\s.*ANALYSIS\n.*</(?:font|b)>\n.*</(?:font|b)>\n\s*</(?:div|p)>',
    '<(?:div|p).*\n.*<(?:font|b)>.*\n.*<(?:font|b).*\n\s*Compensation\s*Discussion\s.*Analysis\n.*</(?:font|b)>\n.*</(?:font|b)>\n\s*</(?:div|p)>'
    ]

# Download all html
def download(path, data_path):
    logging.info("Downloading all html")
    df = pd.read_excel(os.path.join(path,"data.xlsx"))

    htmls = list(df["F"]) # I changed the title in data.xlsx !!!
    ids = list(df["A"])
    if len(ids)!= len(htmls):
        logging.info("Excel file error")
        exit()
    
    for i in range(len(htmls)):
        url = "https://www.sec.gov/Archives/"+htmls[i] 
        os.makedirs(str(ids[i]))
        file_path = os.path.join(data_path, str(ids[i]),str(ids[i])+".txt")
        html_path = os.path.join(data_path, str(ids[i]),str(ids[i])+".html")
        urllib.request.urlretrieve(url, file_path)
        copyfile(file_path, html_path)
        logging.info('{} / {}'.format(i+1, len(htmls)))
    logging.info("Finish download")

# Clean all html
def clean(path, data_path):
    logging.info("Clean all html")
    sys.setrecursionlimit(10000) # Enlarge max recursion limit
    files = os.listdir()
    files =  list(map(int, files))
    files.sort()
    files =  list(map(str, files))
    num = len(files)
    for i in range(num):
        state = False
        write_path = os.path.join(data_path, files[i], files[i]+"_clean.html")
        write_path2 = os.path.join(data_path, files[i], files[i]+"_clean.txt")
        read_path = os.path.join(data_path, files[i], files[i]+".txt")
        f = open(read_path, "r")
        text = f.read()
        f.close()
        clean_text = ""
        try:
            tree = BeautifulSoup(text,"html.parser")
            clean_text = tree.prettify()
            state = True
        except:
            logging.info("file %s html.parser not work", files[i])
        if state is False:
            try:
                tree = BeautifulSoup(text,"lxml")
                clean_text = tree.prettify()
                state = True
            except:
                logging.info("file %s lxml not work", files[i])
        if state is False:
            continue
        f = open(write_path, "w+")
        f.write(clean_text)
        f.close()
        copyfile(write_path, write_path2)
        logging.info('{} / {}'.format(i+1, num))
    logging.info("Finish clean")

# re match
def process(path, data_path):
    global grammar
    success = 0
    files = os.listdir()
    files =  list(map(int, files))
    files.sort()
    files =  list(map(str, files))
    num = len(files) 
    for i in range(num):
        write_path = os.path.join(data_path, files[i], files[i]+"_result.html")
        read_path = os.path.join(data_path, files[i], files[i]+"_clean.txt")
        if os.path.exists(write_path): # Skip if done
            success += 1
            continue
        f = open(read_path, "r")
        text = f.read()
        f.close()
        state = False
        for j in range(len(grammar)): # Try all grammar
            pattern = re.compile(grammar[j])
            match = re.findall(pattern,text)
            if len(match)>1:
                logging.info("file %s need change grammar", files[i])
                logging.info("Follow is all matched", files[i])
                for k in range(len(match)):
                    logging.info(match[k])
                break
            if len(match)==1:
                sen = match[0].split("\n")
                new_grammar = grammar[j]+"[\s\S]*?"+sen[0] # Generate new grammar to catch by hierarchy
                new_pattern = re.compile(new_grammar)
                new_match = re.search(new_pattern,text)
                if not match:
                    logging.info("file %s meet error", files[i])
                    break

                sen = new_match[0].split("\n")
                sen = sen[:-1]
                sen = '\n'.join(sen)
                wf = open(write_path, "w+") # Save result
                wf.write(sen)
                wf.close()
                logging.info("file %s done", files[i])
                state = True
                success += 1
                break

        if state is False:
            logging.info("file %s may not have this part", files[i])
    logging.info("{} / {} success".format(success, num))


def main(path):
    data_path = os.path.join(path, "data")
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        os.chdir(data_path)
        download(path, data_path)
        clean(path, data_path)
    os.chdir(data_path)
    process(path,data_path)
    

if __name__ == '__main__':
    main(path)
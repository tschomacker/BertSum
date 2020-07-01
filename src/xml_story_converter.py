import argparse
from neo4j import GraphDatabase
from collections import Counter
#from models.text import Text
import os
import xml.etree.ElementTree as ET
import sys
import configparser
import os
from os import path
import codecs

parser = argparse.ArgumentParser()
parser.add_argument("-raw_path", default='../raw_data/xml/schaeftlarn')
parser.add_argument("-save_path", default='../raw_data/stories/la')
args = parser.parse_args()

def parse(path_to_file):
    tree = ET.parse(path_to_file)
    root = tree.getroot()
    identifier = ''
    for div in root.iter("{http://www.tei-c.org/ns/1.0}div"):
        if 'n' in div.attrib and 'type' in div.attrib:
            if 'textpart' != div.get('type'):
                identifier = div.get('n')
    regest = ''
    for div in root.iter('{http://www.tei-c.org/ns/1.0}div'):
        if 'subtype' in div.attrib:
            if 'regest' == div.get('subtype'):
                for p in div.iter('{http://www.tei-c.org/ns/1.0}p'):
                    regest = p.text.replace('    ','').replace('\n','')
    text_words = ''
    for text in root.iter('{http://www.tei-c.org/ns/1.0}p'):
        for w in text.iter('{http://www.tei-c.org/ns/1.0}w'):
            if '' != text_words:
                text_words = text_words + ' '
            text_words = text_words + w.text
    if (''== regest):
        print('WARNING: no valid regest found for '+path_to_file)
    return identifier, regest, text_words


def main():
    path =  os.path.abspath(args.raw_path)
    files = []
    # r=root, d=directories, f = files
    print('start to load all formulae from: '+path)
    for r, d, f in os.walk(path):
        for file in f:
            if '.xml' in file:
                if '__cts__.xml' != file and '__capitains__.xml' != file:
                    files.append(os.path.join(r, file))
    count = 0
    for f in files:
        identifier, regest, text = parse(f)
        save_path =  os.path.abspath(args.save_path)
        identifier = identifier.replace(':','.')
        file = codecs.open(save_path+'/'+identifier+'.story', 'w', 'utf-8')
        file.write(text)
        file.write('\n\n@highlight\n\n')
        file.write(regest)
        file.close()
        count += 1
        sys.stdout.write('.')
        if(50==count):
            sys.stdout.write('\n')
        sys.stdout.flush()
    print('\nsuccessfully loaded:', count, 'files')
main()
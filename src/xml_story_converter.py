import argparse
import os
import xml.etree.ElementTree as ET
import sys
import configparser
import os
from os import path
import codecs
import re

parser = argparse.ArgumentParser()
parser.add_argument("-raw_path", default='../raw_data/xml/schaeftlarn')
parser.add_argument("-save_path", default='../raw_data/stories/la')
parser.add_argument('-log_file', default='../logs/converting.log')
parser.add_argument('-verbose', default=False, type=lambda x: (str(x).lower() == 'true'))
args = parser.parse_args()

# xml/html tag regex
TAG_RE = re.compile(r'<[^>]+>')

def parse(path_to_file):
    tree = ET.parse(path_to_file)
    root = tree.getroot()
    identifier = ''
    for div in root.iter("{http://www.tei-c.org/ns/1.0}div"):
        if 'n' in div.attrib and 'type' in div.attrib:
            if 'textpart' != div.get('type'):
                identifier = div.get('n')
    regest = ''
    for front in root.iter('{http://www.tei-c.org/ns/1.0}front'):
        if '{http://www.w3.org/XML/1998/namespace}lang' in front.attrib:
            
            # excluding non-german regests
            if 'deu' == front.get('{http://www.w3.org/XML/1998/namespace}lang'):
                for div in front.iter('{http://www.tei-c.org/ns/1.0}div'):
                    if 'subtype' in div.attrib:
                        if 'regest' == div.get('subtype'):
                            for p in div.iter('{http://www.tei-c.org/ns/1.0}p'):
                                try:
                                    regest = regest + p.text.replace('    ','').replace('\n','')
                                except:
                                    regest = regest
    
    text = ''
    for body in root.iter('{http://www.tei-c.org/ns/1.0}body'):
        for div in body.iter('{http://www.tei-c.org/ns/1.0}div'):
            if 'type' in div.attrib:
                if 'textpart' == div.get('type'):
                    for p in div.iter('{http://www.tei-c.org/ns/1.0}p'):
                        # get the raw text because it includes the punctuation marks
                        # punctuation marks are crucial for the translation quality
                        raw_text = str(ET.tostring(p, encoding="unicode", method="xml"))
                        # remove xml tags
                        raw_text = TAG_RE.sub('', raw_text)
                        
                        raw_text = raw_text.replace('    ','').replace('\n','')
                        text += raw_text + ' '

    return identifier, regest, text


def write_log_file(no_id_found, no_regest_found, no_text_found):
    log_path =  os.path.abspath(args.log_file)
    print('writing the log file to: ',log_path)
    file = codecs.open(log_path, 'w', 'utf-8')
    file.write('no identifier:\n')
    for path in no_id_found:
        file.write('\n'+path)
    file.write('no regest:\n')
    for path in no_regest_found:
        file.write('\n'+path)
    file.write('no text:\n')
    for path in no_text_found:
        file.write('\n'+path)
    file.close()

def get_files(args):
    path =  os.path.abspath(args.raw_path)
    files = []
    # r=root, d=directories, f = files
    print('start to load all formulae from: '+path)
    for r, d, f in os.walk(path):
        for file in f:
            if '.xml' in file:
                if '__cts__.xml' != file and '__capitains__.xml' != file and '.lat' in file:
                    files.append(os.path.join(r, file))
    print('found: '+str(len(files))+ ' files')
    return files

if __name__ == '__main__':
    files = get_files(args)
    count = 0
    no_regest_found = []
    no_id_found = []
    no_text_found = []
    for f in files:
        identifier, regest, text = parse(f)
        if (''== identifier):
            no_id_found.append(f)
        elif (''== regest):
            no_regest_found.append(f)
        elif (''== text):
            no_text_found.append(f)
        else: 
            save_path =  os.path.abspath(args.save_path)
            identifier = identifier.replace(':','.')
            save_path = os.path.join(save_path, identifier+'.story')
            file = codecs.open(save_path, 'w', 'utf-8')
            file.write(text)
            file.write('\n\n@highlight\n\n')
            file.write(regest)
            file.close()
            count += 1
            if args.verbose:
                sys.stdout.write('.')
                if(50==count):
                    print('.')
                    sys.stdout.write('\n')
                sys.stdout.flush()
    write_log_file(no_id_found, no_regest_found, no_text_found)
    print('successfully loaded:', count, 'files. for more info see the log file', )
from googletrans import Translator
import argparse
import os
import codecs

parser = argparse.ArgumentParser()
parser.add_argument("-src_language", default='la', type=str, help='language of the input text')
parser.add_argument("-dest_language", default='de', type=str, help='language of the output text')
parser.add_argument("-raw_path", default='../raw_data/stories/la')
parser.add_argument("-save_path", default='../raw_data/stories/de')
parser.add_argument("-mode", default='pre_highlight', help='pre_highlight or post_highlight')
args = parser.parse_args()


src_language = args.src_language
dest_language = args.dest_language
raw_path = os.path.abspath(args.raw_path)
transalted_stories_dir = os.path.abspath(args.save_path)


def translate(text_file):
    mode = args.mode
    src_language = args.src_language
    dest_language = args.dest_language
    raw_path = os.path.abspath(args.raw_path)
    transalted_stories_dir = os.path.abspath(args.save_path)
    file = codecs.open(raw_path+'/'+text_file, 'r', 'utf-8')
    #reading
    file_text = file.read()
    file.close()
    file_text_array = file_text.split('@highlight')
    #translating
    translator = Translator()
    if('pre_highlight' == mode):
        file_text_array[0] = translator.translate(file_text_array[0], src=src_language, dest=dest_language).text
    elif('post_highlight' == mode):
        file_text_array[1] = translator.translate(file_text_array[1], src=src_language, dest=dest_language).text
    else:
        print('please select a valid mode')
    #writing
    seperator = '/'
    file_name = seperator.join(text_file.rsplit('.', 1)).split(seperator)[0]
    file = codecs.open(transalted_stories_dir+'/'+file_name+'.story', 'w', 'utf-8')
    file.write(file_text_array[0]+'\n\n@highlight'+file_text_array[1])
    file.close()
    return True

from joblib import Parallel, delayed
import time
import multiprocessing


if __name__ == '__main__':
    print("Preparing to translate %s (%s) to %s (%s)..." % (raw_path, src_language, transalted_stories_dir, dest_language))
    texts = os.listdir(raw_path)
    print("Translating %d text(s)..." % (len(texts)))
    start_time = time.time()
    for text_file in texts:
        translate(text_file)
    #Parallel(n_jobs=len(texts))(delayed(translate)(text_file) for text_file in texts)

    print('in ', time.time() - start_time, "seconds")
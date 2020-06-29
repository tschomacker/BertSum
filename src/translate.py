from googletrans import Translator
import argparse
import os
import codecs

parser = argparse.ArgumentParser()
parser.add_argument("-src_language", default='la', type=str, help='language of the input text')
parser.add_argument("-dest_language", default='de', type=str, help='language of the output text')
parser.add_argument("-raw_path", default='../raw_data/stories/la')
parser.add_argument("-save_path", default='../raw_data/stories/de')
args = parser.parse_args()

src_language = args.src_language
dest_language = args.dest_language
raw_path = os.path.abspath(args.raw_path)
transalted_stories_dir = os.path.abspath(args.save_path)

print("Preparing to translate %s (%s) to %s (%s)..." % (raw_path, src_language, transalted_stories_dir, dest_language))
texts = os.listdir(raw_path)
print("Translating %d text(s)..." % (len(texts)))

translator = Translator()
for text_file in texts:
    file = codecs.open(raw_path+'/'+text_file, 'r', 'utf-8')
    text = file.read()
    translation = translator.translate(text, src=src_language, dest=dest_language).text
    file.close()
    seperator = '/'
    file_name = seperator.join(text_file.rsplit('.', 1)).split(seperator)[0]
    file = codecs.open(transalted_stories_dir+'/'+file_name+'.story', 'w', 'utf-8')
    file.write(translation)
    file.close()

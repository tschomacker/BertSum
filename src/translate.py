from googletrans import Translator
import argparse
import os
import codecs
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-src_language", default='la', type=str, help='language of the input text')
parser.add_argument("-dest_language", default='de', type=str, help='language of the output text')
parser.add_argument("-raw_path", default='../raw_data/stories/la')
parser.add_argument("-save_path", default='../raw_data/stories/de')
parser.add_argument('-log_file', default='./logs/translate.log')
parser.add_argument("-mode", default='pre_highlight', help='pre_highlight or post_highlight')
args = parser.parse_args()


src_language = args.src_language
dest_language = args.dest_language
log_file = args.log_file
raw_path = os.path.abspath(args.raw_path)
transalted_stories_dir = os.path.abspath(args.save_path)


def translate_story(text_file, output_file_name):
    mode = args.mode
    src_language = args.src_language
    dest_language = args.dest_language
    
    raw_path = os.path.abspath(args.raw_path)
    file = codecs.open(os.path.join(raw_path,text_file), 'r', 'utf-8')
    #reading
    file_text = file.read()
    file.close()
    file_text_array = file_text.split('@highlight')

    if('pre_highlight' == mode):
        text_part_index = 0
    elif('post_highlight' == mode):
        text_part_index = 1
    else:
        print('please select a valid mode')
        return False

    #translating
    translator = Translator()
    translation = translate_text(os.path.join(raw_path,text_file),translator,file_text_array[text_part_index],src_language,dest_language)
    if translation is None:
        return False
    file_text_array[text_part_index] = translation

    #writing
    file = codecs.open(output_file_name, 'w', 'utf-8')
    file.write(file_text_array[0]+'\n\n@highlight'+file_text_array[1])
    file.close()

def translate_text(file_path,translator,input_text,src_language,dest_language):
    try:
        output_text = translator.translate(input_text, src=src_language, dest=dest_language).text
        if dest_language == translator.detect(output_text).lang:
            return output_text
        else:
            seperators = ['.',',', ' ']
            for seperator in seperators:
                print('batch translate: ',file_path,'with "'+seperator+'" as seperator')
                output_text = translate_by_batch(file_path,translator,input_text,src_language,dest_language,seperator)
                detection = translator.detect(output_text)
                if dest_language == detection.lang:
                    return output_text
                elif src_language != detection.lang:
                    log_translation_warning(file_path,translator,output_text)
                    return output_text
            # previous translation were not successfull
            if output_text is None:
                output_text = ''
            log_translation_error(file_path,translator,output_text)
            return None
    except Exception as e:
        log_translation_catch_exception(file_path,e)
        return None



def log_translation_error(file_path,translator,text):
    log_file = args.log_file
    detection = translator.detect(text)
    file = codecs.open(log_file, 'a', 'utf-8')
    print('translation error')
    file.write(file_path+' seems '+detection.lang+' with a '+str(detection.confidence*100)+'% confidence. It was not translated successfully. Please check manually\n')
    file.close()

def log_translation_warning(file_path,translator,text):
    log_file = args.log_file
    detection = translator.detect(text)
    file = codecs.open(log_file, 'a', 'utf-8')
    print('translation warning')
    file.write(file_path+' seems '+detection.lang+' with a '+str(detection.confidence*100)+'% confidence. But was was nonetheless written to the file. Check in case of doubt\n')
    file.close()

def log_translation_catch_exception(file_path,exception):
    log_file = args.log_file
    file = codecs.open(log_file, 'a', 'utf-8')
    print('translation error')
    file.write(file_path+' throwed '+str(exception)+' Please check manually\n')
    file.close()


# sometimes translating the whole text runs into translation error
# so translation by batches could produce at least a translation
# of many of the batches if not all 
def translate_by_batch(file_path,translator,input_text,src_language,dest_language,seperator):
    translated_text = ''
    batches = str(input_text).split(seperator)
    # filter strings only containing whitespaces and empty strings
    batches = list(filter(lambda x: (not x.isspace() and x), batches))
    # using the bulk translation mode because it only needs one session
    # see https://github.com/ssut/py-googletrans#advanced-usage-bulk
    try:
        for batch in translator.translate(batches, src=src_language, dest=dest_language):
            translated_text = translated_text + batch.text + seperator
        return translated_text
    except Exception as e:
        log_translation_catch_exception(file_path,e)
        return None
    

if __name__ == '__main__':
    print("Preparing to translate %s (%s) to %s (%s)..." % (raw_path, src_language, transalted_stories_dir, dest_language))
    texts = os.listdir(raw_path)
    print("Translating %d text(s)..." % (len(texts)))
    transalted_stories_dir = os.path.abspath(args.save_path)
    file = codecs.open(log_file, 'a', 'utf-8')
    file.write('-----------------------------------\n')
    file.close()
    count = 0
    for text_file in texts:
        seperator = '/'
        output_file_name = seperator.join(text_file.rsplit('.', 1)).split(seperator)[0]
        output_file_name = os.path.join(transalted_stories_dir, output_file_name+'.story')
        #only translate if have not been translated before -> saves time
        if not (os.path.exists(output_file_name)):
            translate_story(text_file,output_file_name)
        count += 1
        if(count % 500 == 0):
            print('translated %d articles' % (count))
    print('translated %d articles' % (count))
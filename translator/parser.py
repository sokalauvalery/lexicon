import re
from PyDictionary import PyDictionary
import time


def get_words(input, known_words=[]):
    new_words = []
    regex = re.compile(r'\b[a-z]+\b')
    for line in input:
        words = regex.findall(line)
        for word in words:
            if word not in known_words:
                new_words.append(word)
    return new_words


def get_words_definition(words, lang=None, interval=1):
    dictionary = PyDictionary()
    translate = {}
    failed_to_define=[]
    for word in words:

        translate[word] = {}
        meaning = dictionary.meaning(word)
        print('Meaning ???  {}'.format((word, meaning)))
        yield (word, meaning)
        # if meaning:
        #     translate[word]['meanings'] = meaning
        # else:
        #     failed_to_define.append(word)
        # if lang:
        #     translate[word]['translate'] = dictionary.translate(word, lang)
        # time.sleep(interval)
        # translate['failed'] = failed_to_define
    #return translate


if __name__ == '__main__':
    with open('/Users/sokalauvalery/Downloads/Peaky.Blinders.S01E01.REPACK.HDTV.x264-TLA.srt') as f:
        #words = get_words(f)[:2]
        words = ['tree',]
        defined_words = get_words_definition(words)
        for word in defined_words:
            print(word)
        print(defined_words)
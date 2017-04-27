import re
from PyDictionary import PyDictionary
import time
# from pymongo import MongoClient
# client = MongoClient('mongo', 27017)
dictionary = PyDictionary()


def get_words(input, known_words=[]):
    new_words = []
    regex = re.compile(r'\b[a-z]+\b')
    for line in input:
        words = regex.findall(line)
        for word in words:
            if word not in known_words:
                new_words.append(word)
    return new_words


class SubSentence:
    def __init__(self, begin_time, end_time, line, block_id=None):
        self.begin_time = begin_time
        self.end_time = end_time
        self.block_id = block_id
        self.line = line
        self.next = None
        self.previous = None

    def __str__(self):
        return '{id} - {begin} : {end} - {line}'.format(id=self.block_id,
                                                        begin=self.begin_time,
                                                        end=self.end_time,
                                                        line=self.line)


class SrtSubParser:
    time_regexp = '(\d\d:\d\d:\d\d),\d\d\d --> (\d\d:\d\d:\d\d),\d\d\d'
    id_regext = '(\d+)'

    def __init__(self, source):
        self.file = source
        self.words = {}

    def parse_line(self, line):
        regex = re.compile(r'\b[a-zA-Z\']+\b')
        return regex.findall(line)

    def get_words(self):
        word_usage_start_time = None
        word_usage_stop_time = None
        block_id = None
        sentence = None
        usage = ''
        for line in self.file:
            line = line.rstrip()
            if not line:
                continue
            time_match = re.match(self.time_regexp, line)
            if time_match:
                sentence = SubSentence(word_usage_start_time, word_usage_stop_time, usage, block_id)
                if usage:
                    words = self.parse_line(usage)
                    for word in words:
                        if word not in self.words:
                            self.words[word] = [sentence]
                            # sentance_position = len(self.words)
                        else:
                            # sentance_position = self.words.index(word)
                            self.words[word].append(sentence)
                        # usage =usage.replace(word, '{' + str(sentance_position) + '}', 1)
                #yield SubSentence(word_usage_start_time, word_usage_stop_time, usage, block_id)
                usage = ''
                word_usage_start_time, word_usage_stop_time = time_match.groups()
                continue
            id_match = re.match(self.id_regext, line)
            if id_match:
                block_id = id_match.groups()[0]
                continue
            usage += ' ' + line
            #yield SubUsage(word_usage_start_time, word_usage_stop_time, usage, block_id)
        return self.words


def get_word_definition(word):
    return dictionary.meaning(word)


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
        subprsr = SrtSubParser(f)
        for line in subprsr.get_words():
            print(line)
        # words = ['tree',]
        # defined_words = get_words_definition(words)
        # for word in defined_words:
        #     print(word)
        # print(defined_words)
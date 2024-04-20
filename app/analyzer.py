import re
import nltk
import string
import pymorphy2

from app.crud import DBCorpusManager
from app.schemas import XmlText, TextMarkup, WordMarkup
from app.llm_api import get_synonyms, get_antonyms, chatting

nltk.download('russian')
nltk.download('popular')


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Analyzer:
    def __init__(self):
        self.morphAnalyzer = pymorphy2.MorphAnalyzer()
        self.stop_words = nltk.corpus.stopwords.words('russian')
        self.bigram_measures = nltk.BigramAssocMeasures()

    def tokenize(self, text):
        result = []
        words = nltk.word_tokenize(text)
        for word in words:
            if (word not in self.stop_words) and (word not in string.punctuation):
                result.append(word)
        return result

    def leksems(self, text):
        leksems = []
        words = self.tokenize(text)
        for word in words:
                leksems.append(self.morphAnalyzer.parse(word)[0].normal_form)
        leksems.sort()
        return leksems

    def analyze(self, text):
        words = self.tokenize(text)
        finder = nltk.BigramCollocationFinder.from_words(
            words)
        finder.apply_freq_filter(1)
        tuple_list = finder.nbest(self.bigram_measures.pmi, 10)
        return list(list(t) for t in zip(*tuple_list))


class CorpusManager(Analyzer, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.db_manager = DBCorpusManager()

    def generate_xml(self, text_obj):
        text_obj = text_obj[0]
        marked_words = []
        text = text_obj.raw_text
        paragraphs = text.split('\n\n')
        text_markup = TextMarkup(version="1.0", encoding="utf-8")
        paragraphs = paragraphs[0].split("\n")
        content = '\n'.join(text.splitlines()[3:])
        text_markup.paragraphs = paragraphs[3:]
        for paragraph in paragraphs[3:]:
            if paragraph not in ['', ' ']:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                text_markup.sentences = sentences
                for sentence in sentences:
                    words_and_punctuation = re.findall(r'\w+|[^\w\s]', sentence)
                    for word_punct in words_and_punctuation:
                        if re.match(r'\w+', word_punct):  # Если это слово
                            morph = pymorphy2.MorphAnalyzer(lang='ru')
                            parsed_word = morph.parse(word_punct)[0].tag.cyr_repr
                            if "ПРИЛ " not in parsed_word and "ЧИСЛ " not in parsed_word:
                                if "," in parsed_word:
                                    parts = parsed_word.split(",", 1)
                                    word = WordMarkup(word=word_punct, lemma=morph.parse(word_punct)[0].normal_form,
                                                      pos=parts[0], gram=parts[1])
                                    marked_words.append(word)
                                else:
                                    word = WordMarkup(word=word_punct, lemma=morph.parse(word_punct)[0].normal_form,
                                                      pos=parsed_word)
                                    marked_words.append(word)
                            else:
                                parts = parsed_word.split(" ", 1)
                                word = WordMarkup(word=word_punct, lemma=morph.parse(word_punct)[0].normal_form,
                                                  pos=parts[0], gram=parts[1])
                                marked_words.append(word)

                        elif word_punct in string.punctuation:
                            word = WordMarkup(word=word_punct)
                            marked_words.append(word)

        xml = XmlText(filename=text_obj.name)
        xml.title = paragraphs[0].split(":")[1].lstrip().rstrip()
        xml.author = paragraphs[1].split(":")[1].lstrip().rstrip()
        xml.tags = paragraphs[2].split(":")[1].lstrip().rstrip()
        xml.words_markup = marked_words
        xml.raw_text = content
        return xml

    def search(self, tag: str, xml: XmlText):
        result = []
        for item in xml.words_markup:
            if item.pos == tag or item.gram == tag:
                result.append(item.word)
        return result
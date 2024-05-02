import re
import nltk
import string
import pymorphy2
from pathlib import Path
import requests
import spacy
from nltk.corpus import stopwords
from spacy import displacy
from app.crud import DBCorpusManager
from app.schemas import XmlText, TextMarkup, WordMarkup

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

    def sentence_analyze(self, text):
        words = self.tokenize(text)
        finder = nltk.BigramCollocationFinder.from_words(
            words)
        finder.apply_freq_filter(1)
        tuple_list = finder.nbest(self.bigram_measures.pmi, 10)
        return list(list(t) for t in zip(*tuple_list))

    def create_svg(self, sentence):
        i = 0
        nlp = spacy.load('ru_core_news_sm')
        doc = nlp(sentence)
        svg = displacy.render(doc, style='dep', jupyter=False)
        filename = 'sentence' + f'{i}' + '.svg'
        output_path = Path(filename)
        output_file = output_path.open('w', encoding='utf-8')
        output_file.write(svg)
        output_file.close()
        i += 1


class CorpusManager(Analyzer, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.db_manager = DBCorpusManager()

    def generate_xml(self, text_obj):
        text_markup_sentences = {}
        text_obj = text_obj[0]
        marked_words = []
        text = text_obj.raw_text
        paragraphs = text.split('\n\n')
        paragraphs = paragraphs[0].split("\n")
        content = '\n'.join(text.splitlines()[3:])
        for paragraph in paragraphs[3:]:
            if paragraph not in ['', ' ']:
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                words = []
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
                                    words.append(word_punct)
                                    marked_words.append(word)
                                else:

                                    word = WordMarkup(word=word_punct, lemma=morph.parse(word_punct)[0].normal_form,
                                                      pos=parsed_word)
                                    words.append(word_punct)
                                    marked_words.append(word)
                            else:
                                parts = parsed_word.split(" ", 1)
                                word = WordMarkup(word=word_punct, lemma=morph.parse(word_punct)[0].normal_form,
                                                  pos=parts[0], gram=parts[1])
                                words.append(word_punct)
                                marked_words.append(word)

                        elif word_punct in string.punctuation:

                            word = WordMarkup(word=word_punct)
                            words.append(word_punct)
                            marked_words.append(word)
                    text_markup_sentences[sentence] = words
                    print(text_markup_sentences)

        xml = XmlText(filename=text_obj.name)
        xml.title = paragraphs[0].split(":")[1].lstrip().rstrip()
        xml.author = paragraphs[1].split(":")[1].lstrip().rstrip()
        xml.tags = paragraphs[2].split(":")[1].lstrip().rstrip()
        xml.text_markup = TextMarkup(sentences=text_markup_sentences)
        xml.words_markup = marked_words
        xml.raw_text = content
        return xml

    def search(self, word: str, xml: XmlText):
        for item in xml.words_markup:
            return item if item.word == word else None

    def get_definition(self, word: str):
        nltk.download('stopwords')
        stop_words = stopwords.words('russian')
        if word.lower() not in stop_words:
            url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{word}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "extract" in data:
                    return data["extract"]
        else:
            return None

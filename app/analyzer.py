import re
import nltk
import string
import pymorphy2

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


class CorpusManager(Analyzer, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self.db_manager = DBCorpusManager()

    def generate_xml(self, text_obj):
        text_obj = text_obj[0]
        text = text_obj.raw_text
        paragraphs = text.split('\n\n')
        text_markup = TextMarkup(version="1.0", encoding="utf-8")
        tagged_text = '<?xml version="1.0" encoding="utf-8"?><text>'
        paragraphs = paragraphs[0].split("\n")
        content = '\n'.join(text.splitlines()[3:])
        text_markup.paragraphs = paragraphs[3:]
        for paragraph in paragraphs[3:]:
            if paragraph not in ['', ' ']:
                tagged_text += '\n <p>'
                # Разбиваем абзац на предложения
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                text_markup.sentences = sentences
                for sentence in sentences:
                    words_and_punctuation = re.findall(r'\w+|[^\w\s]', sentence)  # Разделяем слова и знаки препинания
                    tagged_sentence = ''
                    for word_punct in words_and_punctuation:
                        if re.match(r'\w+', word_punct):  # Если это слово
                            morph = pymorphy2.MorphAnalyzer(lang='ru')
                            parsed_word = morph.parse(word_punct)[0].tag.cyr_repr
                            if "ПРИЛ " not in parsed_word and "ЧИСЛ " not in parsed_word:
                                if "," in parsed_word:
                                    parts = parsed_word.split(",", 1)
                                    morph_tags = f'<ana lemma="{morph.parse(word_punct)[0].normal_form}" pos="{parts[0]}" gram="{parts[1]}"'
                                    word = WordMarkup(word=word_punct, lemma=morph.parse(word_punct)[0].normal_form,
                                                      pos={parts[0]}, gram={parts[1]})
                                else:
                                    morph_tags = f'<ana lemma="{morph.parse(word_punct)[0].normal_form}" pos="{parsed_word}" gram=""'
                                    word = WordMarkup(word=word_punct, lemma=morph.parse(word_punct)[0].normal_form,
                                                      pos={parsed_word}, gram={None})
                            else:
                                parts = parsed_word.split(" ", 1)
                                morph_tags = f'<ana lemma="{morph.parse(word_punct)[0].normal_form}" pos="{parts[0]}" gram="{parts[1]}"'
                                word = WordMarkup(word=word_punct, lemma=morph.parse(word_punct)[0].normal_form,
                                                  pos={parts[0]}, gram={parts[1]})

                            tagged_sentence += f'\n<w>{word_punct} {morph_tags[:-1]}" /></w>'

                        elif word_punct in string.punctuation:  # Если это знак препинания
                            tagged_sentence += f'\n<pun>{word_punct}</pun>'
                            word = WordMarkup(word=word_punct)

                    tagged_sentence = tagged_sentence.strip()  # Удаляем лишние пробелы в конце предложения
                    tagged_sentence = f'\n<s>\n{tagged_sentence}</s>'  # Добавляем тег предложения
                    tagged_text += tagged_sentence

                tagged_text += '</p>'  # Добавляем тег абзаца
        tagged_text += '</text>'
        xml = XmlText(filename=text_obj.name)
        xml.title = paragraphs[0].split(":")[1].lstrip().rstrip()
        xml.author = paragraphs[1].split(":")[1].lstrip().rstrip()
        xml.tags = paragraphs[2].split(":")[1].lstrip().rstrip()
        xml.markup = tagged_text
        xml.raw_text = content
        return xml

    def search(self, tag: str, text_name: str, xml: XmlText):
        pass
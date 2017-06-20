"""Слова длиной меньше 3 не берем, слова дной меньше 2 после стеммера тоже не берем
При наличии большой обучающей выборки создаем второй мешок слов: в одном весь словарный запас, во втором
 только те слова частота которых больше 1 - его и берем для векторизации.
 Можно рассмотреть другие стеммеры
 """
import re
import shelve
import math
from collections import Counter
import numpy as np
from .models import ExpertArticle, Theme, Article
from . import wikilib, config
import random


# удаление чисел и слов длиной меньше 3
def format_word(word_arr):
    alpha = 'АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЪъЫыЬьЭэЮюЯя'
    alpha_set = set(list(alpha))
    new_arr = []
    for word in word_arr:
        word_set = set(list(word))
        compare_set = alpha_set & word_set
        if word.isalpha() and len(word) > 2 and word_set == compare_set:
            new_arr.append(word.lower())
    return new_arr


# сплиттер текста (вход-имя документа, выход-массив слов документа)
def text_split(expert_art_text):
    word_arr = re.split('\W+', expert_art_text)
    word_arr = format_word(word_arr)
    return word_arr


# стеммер (вход-слово, выход-слово)
def stemming(word):
    afix = ["утся", "ётся", "ется", "ются", "ится", "атся", "уться", "ёться",
                    "оться", "яться", "иться", "аться", "еться", "етесь", "итесь",
                    "ась", "усь", "ись", "юсь", "есь", "ему", "ому", "ого", "его", "ать", "ять",
                    "ить", "ыть", "уть", "ете", "ёте", "ешь", "ёшь", "ишь", "ите", "сь", "ся", "ый",
                    "ий", "ая", "яя", "ое", "ее", "ой", "ей", "ом", "ую", "юю", "ым", "им", "ем", "ет",
                    "ёт", "ем", "ём" "ут", "ют", "ит", "им", "ат", "ят", "ой", "ей", "ом", "ем", "ью",
                    "а", "я", "о", "е", "ь", "ы", "и", "й", "у", "ю", "у", "ю"]

    for i in afix:
        word = word.lower()
        if word.endswith(i) and len(word) > 3:
            word = word[0:len(word) - len(i)]
            break
    return word


# стемминг массива слов (вход-массив слов, выход-массив слов)
def stem_arr(word_arr):
    stem_word_arr = []
    for word in word_arr:
        word = stemming(word)
        if len(word) > 1:
            stem_word_arr.append(word)
    return stem_word_arr


# удаление повторяющихся слов(вход-массив слов, выход-массив слов)
def del_repeate(word_arr):
    out_word_arr = []
    for word in word_arr:
        if word not in out_word_arr:
            out_word_arr.append(word)
    return out_word_arr


# массив слов в мешок слов (вход-массив слов)
def word_arr_to_bag(word_arr, path_bag):
    with shelve.open(path_bag) as bag:
        for word in word_arr:
            if word in bag.keys():
                bag[word] += 1
            else:
                bag[word] = 1


# массив слов в вектор (вход-массив слов, выход-вектор)
def word_arr_to_vec(word_arr, path_bag, val_doc):
    word_count_dic = Counter(word_arr)  # словарь повторений слова в входящем массиве слов
    out_vec = []
    with shelve.open(path_bag) as bag:
        keys = bag.keys()
        for key in keys:
            if key in word_count_dic:  # and bag[key] > 1
                n = word_count_dic[key]  # число повторений слова в входящем массиве слов
                val = math.tanh(n / ((bag[key]/val_doc) * 100))  # гиперболический тангенс
                out_vec.append(val)
            else:
                out_vec.append(0)
    return out_vec


# генерация матрицы выходного словя(вход-число массивов, число классов, выход-матрица)
def gen_out_arr(num_arr, num_class):
    Y = np.zeros((num_arr, num_class))
    r = 0
    R = 0
    n = num_arr / num_class
    for c in range(num_class):
        R += n
        while r < R:
            Y[r][c] = 1
            r += 1
    return Y


# размер входного слоя (вход-путь к мешку, выход-размер входного слоя)
def count_keys(path_to_bag):
    count = []
    with shelve.open(path_to_bag) as bag:
        keys = bag.keys()
        print(keys)
        for i in keys:
            count.append(i)
    size = len(count)
    return size


# заполнение мешка слов (вход-путь до документов, путь до мешка)
def fill_bag(expert_art_text, path_to_bag):
        word_arr = text_split(expert_art_text)
        stem_word_arr = stem_arr(word_arr)
        unrep_word_arr = del_repeate(stem_word_arr)
        word_arr_to_bag(unrep_word_arr, path_to_bag)


# векторизация документа(вход-путь до документа, путь до мешка слов, выход-векторы документа и число разбиений)
# преобразует документ в несколько векторов размером n
def fill_vec(expert_art_text, path_to_bag, val_doc, num_word):
    word_arr = text_split(expert_art_text)
    stem_word_arr = stem_arr(word_arr)
    vectors = []
    n = 0
    for arr in range(0, len(stem_word_arr), num_word):
        try:
            stem_word_arr_n = stem_word_arr[arr:arr+num_word]
            vector = word_arr_to_vec(stem_word_arr_n, path_to_bag, val_doc)
            n += 1
        except:
            stem_word_arr_n = stem_word_arr[arr:]
            vector = word_arr_to_vec(stem_word_arr_n, path_to_bag, val_doc)
            n += 1
        finally:
            vectors.append(vector)
    return vectors, n


# вывод результата классификации, усреднение по результатам итераций классификации одного документа
def result_predict(predict_arr):
    try:
        res_predict = [0 for i in range(len(predict_arr[0]))]
        for arr in predict_arr:
            for i in range(len(arr)):
                res_predict[i] += arr[i]
        for i in range(len(res_predict)):
            res_predict[i] = res_predict[i] / len(predict_arr)
    except TypeError:
        res_predict = predict_arr
    return res_predict


def get_expert_list():
    expert_list = []
    expert_arts = ExpertArticle.objects.all()
    expert_list = list(expert_arts)
    return expert_list


def get_list_fit_and_test():
    themes = Theme.objects.all()
    expert_list_fit = []
    expert_list_test = []
    for theme in themes:
        expert_list = ExpertArticle.objects.filter(expert_themes=theme)
        list_fit = random.sample(list(expert_list), len(expert_list) - 1)
        if len(list_fit) == 0:
            list_fit = expert_list
            for art_fit in list_fit:
                expert_list_fit.append(art_fit)
        else:
            list_test = list(set(expert_list) - set(list_fit))
            for art_fit in list_fit:
                expert_list_fit.append(art_fit)
            for art_test in list_test:
                expert_list_test.append(art_test)
    return expert_list_fit, expert_list_test


def get_num_class():
    num_class = Theme.objects.all().last().id
    return num_class


def get_val_doc():
    val_doc = len(ExpertArticle.objects.all())
    return val_doc


def check_art():
    art_arr = Article.objects.all()
    art_list = []
    for art in art_arr:
        if len(art.themes.all()) == 0:
            art_list.append(art)
    print(3)
    return art_list


# получение новых статей из википедии для обучающей выборки на основе неклассифицированных статей пользователей
# в виде списка словарей, где ключи - это темы
def get_new_expert_art(art_list):
    path_to_bag = config.load_config()
    list_dicts_pages = []
    for art in art_list:
        print(art.article_title)
        dict_pages = wikilib.get_dict_wiki_page(art.article_text, path_to_bag)
        list_dicts_pages.append(dict_pages)
        print(list_dicts_pages)
    print(6)
    return list_dicts_pages


# добавление новых статей из википедии в обучающую выборку
def add_new_expert_art(list_dicts_pages):
    for page_dict in list_dicts_pages:
        for theme in page_dict:
            try:
                new_theme = Theme(theme_name=theme)
                new_theme.save()
                list_pages = page_dict[theme]
                for page in list_pages:
                    new_expert_art = ExpertArticle(expert_art_title=page.title,
                                                   expert_art_text=page.content,
                                                   expert_themes=new_theme)
                    new_expert_art.save()
            except:
                continue
    print(5)


# получение и добавление новых статей из википедии на основе списка неклассифицированных пользовательских статей
def get_and_add_new_expert_art(art_list):
    list_dicts_pages = get_new_expert_art(art_list)
    add_new_expert_art(list_dicts_pages)
    print(4)

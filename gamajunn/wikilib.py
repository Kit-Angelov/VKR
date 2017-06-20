"""1. Берем термины которых нет в мешке слов
   2. Ищем по каждому страницу в wiki
   3. Вытаскиваем категории каждой страницы, фильтруем их
   4. Ищем по каждой категории список страниц wiki
   5. Категория становится новым классом в инс,
                    а каждая статья из wiki по данной категории добавляется
                                    в обучающуу выборку для обучения нового класса
   6. Есть возможность реализации поискового паука,
                    если из каждой последующей статьи по категории доставать новые категории"""


import wikipedia as wiki
import re
import shelve
from gamajunn import utils, config
from collections import Counter


# вывод незнакомых мешку слов
def preparation_text(art_text, path_to_bag):
    bag = shelve.open(path_to_bag)
    keys = bag.keys()
    low_reg_word_arr = utils.text_split(art_text)
    stem_word_arr = utils.stem_arr(low_reg_word_arr)
    compare = []
    for i in stem_word_arr:
        if i not in keys:
            compare.append(i)
    print(compare)
    res_unknown_arr = []
    for b in compare:
        for a in low_reg_word_arr:
            if a.startswith(b):
                res_unknown_arr.append(a)
                break
    print(10)
    print(res_unknown_arr)
    return res_unknown_arr


# поиск категорий и их фильтр по незнакомым словам
def search_theme(res_unknown_arr):
    themes_arr = []
    res_themes_arr = []
    for word in res_unknown_arr:
        try:
            wiki.set_lang("ru")
            page = wiki.page(word)
            cat = page.categories
            for item in cat:
                themes_arr.append(item)
        except:
            continue
    count_themes = Counter(themes_arr)
    for c in count_themes:
        c_split = re.split('\W+', c)
        if '' in c_split:
            c_split.remove('')
        c_set = set(c_split)
        c_lower_set = {i.lower() for i in c_set}
        if (count_themes[c] >= config.min_count) and not(c_lower_set & config.correct_set) \
                and not(c_split[1].endswith('и') or c_split[1].endswith('ы')) \
                and (len(c_split) < 4):
            if len(c_split) < 3:
                res_themes_arr.append(c)
            elif not c_split[2].istitle():
                res_themes_arr.append(c)
    print(9)
    print(res_themes_arr)
    return res_themes_arr


# поиск статей по полученным категориям для добавления в обучающую выборку
def get_art_for_fit(res_themes_arr):
    dict_wiki_page = {}
    for theme in res_themes_arr:
        theme = theme[10:]
        dict_wiki_page[theme] = []
        wiki.set_lang('ru')
        wiki_search_res = wiki.search(theme)
        for title_page in wiki_search_res:
            try:
                page = wiki.page(title_page)
                dict_wiki_page[theme].append(page)
            except:
                continue
    print(8)
    print(dict_wiki_page)
    return dict_wiki_page


# получение нового списка страниц википедии на основе неклассифицированной статьи пользователя
def get_dict_wiki_page(art_text, path_to_bag):
    res_unknown_arr = preparation_text(art_text, path_to_bag)
    res_themes_arr = search_theme(res_unknown_arr)
    dict_wiki_page = get_art_for_fit(res_themes_arr)
    print(7)
    return dict_wiki_page

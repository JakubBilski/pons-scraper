import requests
import csv

from bs4 import BeautifulSoup


def find_best_plural_form(word, suffix):
    len_w = len(word)
    len_s = len(suffix)
    best_offset = len_w
    best_offset_score = 1
    for offset in range(max(0, len_w - len_s), len_w):
        offset_score = sum([word[offset+i] == suffix[i] for i in range(min(len_s, len_w-offset))])
        if offset_score > best_offset_score:
            best_offset = offset
            best_offset_score = offset_score
    return '<span style="background-color:rgb(255,122,154)">die</span> '+ word[:best_offset] + suffix


def parse_noun(word_romhead, word_h2):
    translation = ' '.join([a.text for a in word_romhead.find(class_='target').findAll('a', recursive=False)]).replace('  ', ' ')
    if "r.m." in word_h2.text:
        article = '<span style="background-color:rgb(146,196,255)">der</span>'
    elif "r.ż." in word_h2.text:
        article = '<span style="background-color:rgb(255,122,154)">die</span>'
    else:
        article = '<span style="background-color:rgb(255,231,161)">das</span>'
    word_div = [
        div for div in word_romhead.findAll(class_='translations')
    ][0]
    word = ' '.join([
        a.text for a in word_div.findAll(
            class_='headword'
        )[0]
    ])
    flexion_text = word_h2.find(class_='flexion').text
    plural_suffix = flexion_text[flexion_text.index(',')+2:-1]
    if ';' in plural_suffix:
        plural_suffix = plural_suffix[:plural_suffix.index(';')]
    if ',' in plural_suffix:
        plural_suffix = plural_suffix[:plural_suffix.index(',')]
    if plural_suffix[0] == '‑':
        plural_form = find_best_plural_form(word, plural_suffix[1:])
    elif 'bez l.mn.' in plural_suffix:
        plural_form = '-'
    else:
        plural_form = '<span style="background-color:rgb(255,122,154)">die</span> ' + plural_suffix
    zwroty_divs = [
        div for div
        in word_romhead.findAll(class_='translations')
        if 'zwroty' in div.find('h3').text
    ]
    if len(zwroty_divs) == 0:
        return translation, f'<span style="font-size: 1.2em">{article} {word}, {plural_form}</span><br>'
    zwrot = ' '.join([
        a.text for a in zwroty_divs[0].findAll(
            class_='source'
        )[0].findAll('span')[0].findAll(['a', 'strong'])
    ])
    zwrot = zwrot.replace('  ', ' ')

    zwrot_translation = ' '.join([
        a.text for a in zwroty_divs[0].findAll(
            class_='target'
        )[0].findAll('a')
    ])
    zwrot_translation = zwrot_translation.replace('  ', ' ')
    return translation, f'<span style="font-size: 1.2em">{article} {word}, {plural_form}</span><br><br>{zwrot}<br>({zwrot_translation})<br>'


def parse_verb(word_romhead, word_h2):
    translation = ' '.join([a.text for a in word_romhead.find(class_='target').findAll('a', recursive=False)]).replace('  ', ' ')
    word_div = [
        div for div in word_romhead.findAll(class_='translations')
    ][0]
    # word = ' '.join([
    #     a.text for a in word_div.findAll(
    #         class_='source'
    #     )[0].findAll(['a', 'strong'])
    # ])
    if len(word_div.findAll(class_='headword')) > 0:
        word = ' '.join([
            a.text for a in word_div.findAll(
                class_='headword'
            )[0]
        ])
    elif len(word_div.findAll(class_='example')) > 0:
        word = ' '.join([
            a.text for a in word_div.findAll(class_='example')[0].findAll(['a', 'strong'], recursive=False)
        ])
    else:
        raise Exception("Unrecognized source word type")
    if 'cz. przech.' in word_h2.find(class_='verbclass').text:
        word += ' +A'
    if len(word_h2.findAll(class_='flexion')) > 0:
        flexion = word_h2.find(class_='flexion').text[1:-1]
        flexion = f'<br><span style="color:gray">{flexion}</span>'
    else:
        flexion = ''
    zwroty_divs = [
        div for div
        in word_romhead.findAll(class_='translations')
        if 'zwroty' in div.find('h3').text
    ]
    if len(zwroty_divs) == 0:
        return translation, f'<span style="font-size: 1.2em">{word}</span>{flexion}'
    zwrot = ' '.join([
        a.text for a in zwroty_divs[0].findAll(
            class_='source'
        )[0].findAll('span')[0].findAll(['a', 'strong'])
    ])
    zwrot = zwrot.replace('  ', ' ')

    zwrot_translation = ' '.join([
        a.text for a in zwroty_divs[0].findAll(
            class_='target'
        )[0].findAll('a')
    ])
    zwrot_translation = zwrot_translation.replace('  ', ' ')
    return translation, f'<span style="font-size: 1.2em">{word}</span>{flexion}<br><br>{zwrot}<br>({zwrot_translation})<br>'


def parse_any_other(word_romhead, word_h2):
    translation = ' '.join([a.text for a in word_romhead.find(class_='target').findAll('a', recursive=False)]).replace('  ', ' ')
    word_div = [
        div for div in word_romhead.findAll(class_='translations')
    ][0]
    # word = ' '.join([
    #     a.text for a in word_div.findAll(
    #         class_='source'
    #     )[0].findAll(['a', 'strong'])
    # ])
    if len(word_div.findAll(class_='headword')) > 0:
        word = ' '.join([
            a.text for a in word_div.findAll(
                class_='headword'
            )[0]
        ])
    elif len(word_div.findAll(class_='example')) > 0:
        word = ' '.join([
            a.text for a in word_div.findAll(class_='example')[0].findAll(['a', 'strong'], recursive=False)
        ])
    else:
        raise Exception("Unrecognized source word type")
    return translation, f'<span style="font-size: 1.2em">{word}</span>'


def create_card(word):
    url = f"https://pl.pons.com/t%C5%82umaczenie/niemiecki-polski/{word}"
    try:
        page = requests.get(url)
    except:
        #  print(f"Unable to get {word}, site {url} doesn't respond")
        return None, None
    soup = BeautifulSoup(page.content, "html.parser")
    front = ''
    reverse = ''

    word_romheads = soup.findAll(class_="rom first")
    #  print(f"Found {len(word_romheads)} candidate romheads")
    questions = []
    answers = []

    user_added_romheads = [rh for rh in word_romheads if "ytkownika" in rh.text]
    not_user_added_romheads = [rh for rh in word_romheads if "ytkownika" not in rh.text]
    word_romheads = not_user_added_romheads
    word_romheads.extend(user_added_romheads)  # user-created translations are a last resort

    for word_romhead in word_romheads:
        word_h2 = word_romhead.find("h2")
        word_class = word_h2.find(class_='wordclass').text
        if 'CZ.' in word_class:
            try:
                question, answer = parse_verb(word_romhead, word_h2)
            except:
                continue
        elif 'RZ.' in word_class:
            try:
                question, answer = parse_noun(word_romhead, word_h2)
            except:
                continue
        else:
            try:
                question, answer = parse_any_other(word_romhead, word_h2)
            except:
                continue
        if question in questions:
            continue
        questions.append(question)
        answers.append(answer)
        if len(questions) > 1:
            break

    if len(questions) == 0:
        print(f"Unable to parse any of the {len(word_romheads)} sections! Skipping the word")
        return None, None

    for i, q in enumerate(questions):
        front += f'{i+1}: {q}<br>'

    for i, a in enumerate(answers):
        reverse += f'{a}<br><br>'
    
    return front, reverse


def load_input(filepath):
    f = open(filepath, 'r', encoding="utf-8")
    words = f.readlines()
    return words


if __name__ == '__main__':
    fronts = []
    reverses = []
    words = load_input('input.txt')
    for word in words:
        print(f"{word}", end='')
        # try:
        front, reverse = create_card(word)
        # except Exception as e:
        #     print("Wasn't able to parse because of the following error:")
        #     print(e)
        #     continue
        if front is not None:
            fronts.append(front)
            reverses.append(reverse)

    with open('output.csv', 'w', newline='', encoding="utf-8") as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for f, r in zip(fronts, reverses):
            spamwriter.writerow([f, r])

import requests
import csv

from tqdm import tqdm
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
    return 'die '+ word[:best_offset] + suffix


def parse_noun(word_romhead, word_h2):
    translation = ' '.join([a.text for a in word_romhead.find(class_='target').findAll('a', recursive=False)]).replace('  ', ' ')
    if "r.m." in word_h2.text:
        article = "der"
    elif "r.ż." in word_h2.text:
        article = "die"
    else:
        article = "das"
    is_zenski = "r.ż." in word_romhead.find(class_='target').text
    word = str(word_h2)
    word = word[word.index('>')+1:]
    word = word[:word.index('<')]
    word = word.replace(' ', '')
    word = word.replace('\n', '')
    flexion_text = word_h2.find(class_='flexion').text
    plural_suffix = flexion_text[flexion_text.index(',')+2:-1]
    if plural_suffix[0] == '‑':
        plural_form = find_best_plural_form(word, plural_suffix[1:])
    elif 'bez l.mn.' in plural_suffix:
        plural_form = '-'
    else:
        plural_form = 'die ' + plural_suffix
    zwroty_divs = [
        div for div
        in word_romhead.findAll(class_='translations')
        if 'zwroty' in div.find('h3').text
    ]
    if len(zwroty_divs) == 0:
        return translation, f"{article} {word}, {plural_form}\n"
    else:
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
        return translation, f"{article} {word}, {plural_form}\n\n{zwrot}\n({zwrot_translation})\n"


def parse_verb(word_romhead, word_h2):
    translation = ' '.join([a.text for a in word_romhead.find(class_='target').findAll('a', recursive=False)]).replace('  ', ' ')
    word = ' '.join([x.text for x in word_h2.findAll(string=True, recursive=False)])
    word = word.replace(' ', '')
    word = word.replace('\n', '')
    return translation, word


def create_card(word):
    url = f"https://pl.pons.com/t%C5%82umaczenie/niemiecki-polski/{word}"
    try:
        page = requests.get(url)
    except:
        print(f"Unable to get {word}, site {url} doesn't respond")
        return None, None
    soup = BeautifulSoup(page.content, "html.parser")
    front = ''
    reverse = ''

    word_romheads = soup.findAll(class_="rom first")
    questions = []
    answers = []

    for word_romhead in word_romheads:
        if "ytkownika" in word_romhead.text:
            # skip user-created translations
            continue
        word_h2 = word_romhead.find("h2")
        word_class = word_h2.find(class_='wordclass').text
        if 'CZ.' in word_class:
            question, answer = parse_verb(word_romhead, word_h2)
        elif 'RZ.' in word_class:
            question, answer = parse_noun(word_romhead, word_h2)
        else:
            continue
        questions.append(question)
        answers.append(answer)
        if len(questions) > 1:
            break

    for i, q in enumerate(questions):
        front += f'{i+1}: {q}\n'

    for i, a in enumerate(answers):
        reverse += f'{a}\n\n'
    
    return front, reverse


def load_input(filepath):
    f = open(filepath, 'r')
    words = f.readlines()
    return words


if __name__ == '__main__':
    fronts = []
    reverses = []
    words = load_input('input.txt')
    for word in tqdm(words):
        front, reverse = create_card(word)
        if front is not None:
            fronts.append(front)
            reverses.append(reverse)

    with open('output.csv', 'w', newline='', encoding="utf-8") as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for f, r in zip(fronts, reverses):
            spamwriter.writerow([f, r])

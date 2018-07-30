import os
from pathlib import Path
from local_pybo import *
import time

tok = BoTokenizer('POS')


def get_tokens(filename):
    print(filename, '\n\tTokenizing...')
    with open(filename) as f:
        dump = f.read()
    start = time.time()
    tokens = tok.tokenize(dump)
    end = time.time()
    print('\tTime:', end-start)
    return tokens


def get_antconc_format(tokens):
    out = []
    aa = False
    for token in tokens:
        if token.affixed:
            if token.aa_word:
                aa = True
            out.append(token.unaffixed_word)
        elif token.affix:
            if aa:
                out.append('-' + token.cleaned_content)
                aa = False
            else:
                out.append('+' + token.cleaned_content)
        elif token.type != 'syl':
            out.append(token.content)
        else:
            out.append(token.cleaned_content)
    return ' '.join(out)


def get_lemmatized(tokens):
    out = [token.lemma if token.type == 'syl' else token.content for token in tokens]
    return ' '.join(out)


def get_cleaned(tokens):
    out = [token.cleaned_content if token.type == 'syl' else token.content for token in tokens]
    return ' '.join(out)


def process(tokens, treatment, treatment_name, collection):
    treated = treatment(tokens)
    out_filename = 'segmented'
    for level in ['', collection, treatment_name]:
        out_filename += level + '/'
        level_path = Path(out_filename)
        level_path.mkdir(parents=True, exist_ok=True)

    out_filename += filename
    with open(out_filename, 'w') as f:
        f.write(treated)
    print('Processed.')


def process_volume(folder, filename, collection):
    tokens = get_tokens(folder + filename)
    process(tokens, get_antconc_format, 'antconc', collection)
    process(tokens, get_lemmatized, 'lemmatized', collection)
    process(tokens, get_cleaned, 'cleaned', collection)


if __name__ == '__main__':
    # kangyur
    kangyur_folder = 'files/k/'
    filenames = os.listdir(kangyur_folder)
    for filename in filenames:
        process_volume(kangyur_folder, filename, 'k')

    # tengyur
    tengyur_folder = 'files/t/'
    filenames = os.listdir(tengyur_folder)
    for filename in filenames:
        process_volume(tengyur_folder, filename, 't')

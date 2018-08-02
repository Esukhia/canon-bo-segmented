from pathlib import Path
from pybo import *
import time

tok = BoTokenizer('POS')


def get_tokens(filename):
    print(filename, '\n\tTokenizing...', end=' ')
    dump = filename.read_text(encoding='utf-8-sig')
    start = time.time()
    tokens = tok.tokenize(dump)
    end = time.time()
    print('({:.0f}s.)'.format(end-start))
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


def get_antconc_pos(tokens):
    out = []
    aa = False
    for token in tokens:
        if token.affixed:
            if token.aa_word:
                aa = True
            out.append('{}_{}'.format(token.unaffixed_word, token.pos))
        elif token.affix:
            if aa:
                out.append('{}_{}'.format('-' + token.cleaned_content, token.pos))
                aa = False
            else:
                out.append('{}_{}'.format('+' + token.cleaned_content, token.pos))
        elif token.type != 'syl':
            out.append('{}_{}'.format(token.content, token.pos))
        else:
            out.append('{}_{}'.format(token.cleaned_content, token.pos))
    return ' '.join(out)


def get_lemmatized(tokens):
    out = [token.lemma if token.type == 'syl' else token.content for token in tokens]
    return ' '.join(out)


def get_cleaned(tokens):
    out = [token.cleaned_content if token.type == 'syl' else token.content for token in tokens]
    return ' '.join(out)


def process(tokens, treatment, treatment_name, collection):
    treated = treatment(tokens)
    out_path = Path('segmented') / collection / treatment_name / filename.name
    for parent in reversed(out_path.parents):
        parent.mkdir(parents=True, exist_ok=True)

    out_path.write_text(treated, encoding='utf-8-sig')
    print('\t\tProcessed', out_path.parts[2])


def process_volume(filename, collection):

    tokens = get_tokens(filename)
    process(tokens, get_antconc_format, 'antconc', collection)
    process(tokens, get_lemmatized, 'lemmatized', collection)
    process(tokens, get_cleaned, 'cleaned', collection)
    process(tokens, get_antconc_pos, 'antconc-pos', collection)


if __name__ == '__main__':
    # kangyur
    kangyur_folder = 'files/k/'
    filenames = os.listdir(kangyur_folder)

    # for filename in filenames[10:11]:
    for filename in filenames:
        if not filename.startswith('.'):
            process_volume(kangyur_folder, filename, 'k')

    # tengyur
    tengyur_folder = 'files/t/'
    filenames = os.listdir(tengyur_folder)
    for filename in filenames:
        if not filename.startswith('.'):
            process_volume(tengyur_folder, filename, 't')

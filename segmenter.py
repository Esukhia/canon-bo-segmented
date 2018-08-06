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


def get_skrt_pos(token):
    if token.skrt:
        return 'SKRT'
    else:
        return token.pos


def get_antconc_pos(tokens):
    out = []
    aa = False
    for token in tokens:
        if token.affixed:
            if token.aa_word:
                aa = True
            out.append('{}_{}'.format(token.unaffixed_word, get_skrt_pos(token)))
        elif token.affix:
            if aa:
                out.append('{}_{}'.format('-' + token.cleaned_content, get_skrt_pos(token)))
                aa = False
            else:
                out.append('{}_{}'.format('+' + token.cleaned_content, get_skrt_pos(token)))
        elif token.type != 'syl':
            out.append('{}_{}'.format(token.content, get_skrt_pos(token)))
        else:
            out.append('{}_{}'.format(token.cleaned_content, get_skrt_pos(token)))
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
    kangyur = 'k'
    k_folder = Path('files') / kangyur
    for filename in list(k_folder.glob('*.txt'))[98:99]:
        process_volume(filename, kangyur)

    tengyur = 't'
    t_folder = Path('files') / tengyur
    for filename in list(t_folder.glob('*.txt'))[20:21]:
        process_volume(filename, tengyur)

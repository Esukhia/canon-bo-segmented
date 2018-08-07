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
            word = token.unaffixed_word
        elif token.affix:
            if aa:
                word = '-' + token.cleaned_content
                aa = False
            else:
                word = '+' + token.cleaned_content
        elif token.type != 'syl':
            word = token.content
        else:
            word = token.cleaned_content

        word = word.replace(' ', '')
        out.append(word)

    return ' '.join(out)


class FindPos:
    def __init__(self):
        pass

    def find_pos(self, token):
        if self.is_skrt_word(token):
            return 'SKRT'
        elif self.is_return(token):
            return ''
        elif self.is_toh(token):
            return ''
        else:
            return token.pos

    @staticmethod
    def is_skrt_word(token):
        return token.skrt and (token.pos == 'OOV'
                               or token.pos == 'oov'
                               or token.pos == 'non-word'
                               or token.pos == 'X'
                               or token.pos == 'syl')

    @staticmethod
    def is_return(token):
        return token.content == '\n'

    @staticmethod
    def is_toh(token):
        return token.content.startswith('T') \
               or token.content.lstrip('\n').startswith('T')


def get_antconc_pos(tokens):
    sep = '_'
    fp = FindPos()
    out = []
    aa = False
    for token in tokens:
        if token.affixed:
            if token.aa_word:
                aa = True
            word = token.unaffixed_word
        elif token.affix:
            if aa:
                word = '-' + token.cleaned_content
                aa = False
            else:
                word = '+' + token.cleaned_content
        elif token.type != 'syl':
            word = token.content
        else:
            word = token.cleaned_content

        pos = fp.find_pos(token)
        word = word.replace(' ', '')
        if pos:
            out.append(f'{word}{sep}{pos}')
        else:
            out.append(word)
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
    for filename in sorted(list(k_folder.glob('*.txt')))[98:99]:
        process_volume(filename, kangyur)
    #
    # tengyur = 't'
    # t_folder = Path('files') / tengyur
    # for filename in list(t_folder.glob('*.txt'))[20:21]:
    #     process_volume(filename, tengyur)

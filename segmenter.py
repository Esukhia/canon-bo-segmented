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


class GetAntconcFormat:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tokens_len = len(self.tokens)
        self.key = 'antconc'

    def apply(self):
        self.prepare()
        self.find_content()
        self.mark_affixed_particles()
        return self.tokens

    def prepare(self):
        for i in range(self.tokens_len):
            self.tokens[i]._[self.key] = {}

    def find_content(self):
        for token in self.tokens:
            if token.affixed:
                token._[self.key]['word'] = token.unaffixed_word
            elif token.type != 'syl':
                token._[self.key]['word'] = token.content
            else:
                token._[self.key]['word'] = token.cleaned_content

            token._[self.key]['word'] = self.clean_word(token._[self.key]['word'])

    def mark_affixed_particles(self):
        for num, token in enumerate(self.tokens):
            if self.tokens[num - 1].affixed and token.affix:
                if token.aa_word:
                    token._[self.key]['word'] = '-' + token._[self.key]['word']
                else:
                    token._[self.key]['word'] = '+' + token._[self.key]['word']

    @staticmethod
    def clean_word(word):
        word = word.replace(' ', '')
        return word


class GetAntconcPos(GetAntconcFormat):
    def __init__(self, tokens):
        super().__init__(tokens)
        self.key = 'antpos'

    def apply(self):
        self.prepare()
        self.find_content()
        self.mark_affixed_particles()
        self.find_pos()
        return self.tokens

    def find_pos(self):
        for token in self.tokens:

            if self.is_skrt_word(token):
                token._[self.key]['pos'] = 'SKRT'

            elif self.is_return(token) \
                    or self.is_toh(token):
                token._[self.key]['pos'] = ''

            else:
                token._[self.key]['pos'] = token.pos

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


def get_lemmatized(tokens):
    key = 'lemmatized'
    for token in tokens:
        token._[key] = {}   # initialize custom data for this token
        if token.type == 'syl':
            token._[key]['word'] = token.lemma
        else:
            token._[key]['word'] = token.content
    return tokens


def get_cleaned(tokens):
    key = 'cleaned'
    for token in tokens:
        token._[key] = {}   # initialize custom data for this token
        if token.type == 'syl':
            token._[key]['word'] = token.cleaned_content
        else:
            token._[key]['word'] = token.content
    return tokens


def generate_output(tokens, treatment):
    sep = '_'
    out = []
    for token in tokens:
        if 'pos' in token._[treatment].keys():
            if token._[treatment]['pos']:
                out.append(f"{token._[treatment]['word']}{sep}{token._[treatment]['pos']}")
            else:
                out.append(token._[treatment]['word'])
        else:
            out.append(token._[treatment]['word'])
    return ' '.join(out)


def write_to_file(tokens, collection):
    treatments = list(tokens[0]._.keys())

    for treatment in treatments:
        # create directories
        out_path = Path('segmented') / collection / treatment / filename.name
        for parent in reversed(out_path.parents):
            parent.mkdir(parents=True, exist_ok=True)

        treated = generate_output(tokens, treatment)

        out_path.write_text(treated, encoding='utf-8-sig')


def process_volume(filename, collection):
    tokens = get_tokens(filename)

    tokens = GetAntconcFormat(tokens).apply()
    tokens = GetAntconcPos(tokens).apply()
    tokens = get_lemmatized(tokens)
    tokens = get_cleaned(tokens)

    write_to_file(tokens, collection)


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

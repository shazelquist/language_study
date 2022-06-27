"""
# test_ray.py
#
# Directive:
#   Proof of concept in known language
#   Provide interface for testing concepts in ray
"""
# Shane_Hazelquist #Date: Monday, 6/20/2022  #Time: 23:17.54
# Imports:
import re
from ray import *


class pseudo_db:
    """
    pseudo_db

    container for proof of concept searches
    """

    def __init__(self):
        """
        __init__()

        establishes container
        """
        self.cont = {}

    def __obj_label__(self, obj, label=None):
        """
        __obj_label__(obj, label)

        determines if object or label
        """
        if type(label) != type("") or not label:
            label = type(obj)
        return label

    def add(self, obj, label=None):
        """
        add(obj, label='')

        adds object to collection
        """
        label = self.__obj_label__(obj, label)
        if label not in self.cont.keys():
            self.cont[label] = []
        self.cont[label].append(obj)

    def add_all(self, obj, label=None):
        """
        add_all(obj)

        adds all objects in given iterable
        """
        label = self.__obj_label__(obj, label)
        for item in obj:
            self.add(item, label)

    def query(self, label, cond):
        """
        query(label, cond)

        returns all sucessful conditions for obj type
        """
        label = self.__obj_label__(label, label)
        return [item for item in self.cont[label] if cond(item)]

    def count(self, label, cond):
        """
        count(label, cond)

        returns number of sucessful conditions
        """
        label = self.__obj_label__(label, label)
        return sum([1 for item in self.cont[label] if cond(item)])

    def first(self, label, cond):
        """
        first(label, cond)

        returns first match to condition for obj type
        """
        label = self.__obj_label__(label, label)
        for item in self.cont[label]:
            if cond(item):
                return item

p_db = pseudo_db()


def floor(arg):
    """
    floor(arg)

    return the floor of that number IE, round down
    """
    res = int(arg)
    if res > arg:
        res -= 1
    return res


def getindex(xchr, ychr, chars):
    """
    getindex(xchr, ychr, chars)

    return the 1d index of column character x and row character y
    """
    ypos = chars.index(ychr)
    xpos = chars.index(xchr)
    return ypos * len(chars) + xpos


def getcolsum(xchr, matrix, chars):
    """
    getcolsum(xchr, matrix, chars)

    return the sum of a given x character's column
    """
    xpos = chars.index(xchr)
    sumval = sum([matrix[getindex(xchr, i, chars)] for i in chars[:-2]])
    if not sumval:
        # basically, if this is the last token/character, there is no child so it's fine
        #print('\nerror on x_pos {}\n{}'.format(xchr, matrix))
        #print('\n'.join([str(j) for j in [matrix[getindex(xchr, i, chars)] for i in chars[:-2]]]))
        return 1
    return sumval


def printmatrix(chars, matrix):
    """
    printmatrix(chars, matrix)

    print the matrix with some degree of formatting
    note:
        Formatting not good enough to directly port to csv
    """
    ends = " "
    print(ends.join(['"{}"'.format(i) for i in ["N"] + chars]))
    # print('{} '.format(chars[0]),end='')
    f_format = '"{}"'# '"{}"'  # '{:.1f}'
    colsums = [getcolsum(i, matrix, chars) for i in chars] + [1, 1]
    for i in range(0, len(matrix)):
        if i % len(chars) == 0:
            print(
                '{}"{}"'.format("\n" * (i != 0), chars[floor(i / len(chars))]), end=ends
            )
        if i % len(chars) == len(chars) - 1 or i % len(chars) == len(chars) - 2:
            print(f_format.format(matrix[i]), end=ends)
        elif colsums[i % len(chars)]:
            print(f_format.format(matrix[i] / colsums[i % len(chars)]), end=ends)
        else:
            print(f_format.format(matrix[i]), end=ends)
    print("\n", end="")

def matrix_and_count(tokens, label_c, label_r, components=None, matrix=None):
    """
    matrix_and_count(tokens, label_c, label_r)

    tokens:  list of tokens
    label_c: label for compoenent storage
    label_r: label for relation storage
    """
    if not components:
        components = list(set(tokens))
        components.sort()
        components.append("$")
        components.append("^")

    if not matrix:# add tokens to components, if not already done through implication
        token_obj = [syllabary(c, tokens.count(c)) for c in components]
        p_db.add_all(token_obj, label_c)

    ptext = ["^"] + tokens + ["$"]
    if not matrix:
        matrix = [0] * (len(components) * (len(components) - 2))
    # printmatrix(chars,matrix)
    for i in range(1, len(tokens) + 1):
        matrix[getindex(ptext[i - 1], ptext[i], components)] += 1
        pass
    matrix[getindex("$", tokens[-1], components)] += 1

    relations = []
    colsums = [getcolsum(i, matrix, components) for i in components] + [1, 1]
    for i in range(0, len(matrix)):
        if matrix[i]:
            parent = p_db.first(label_c, lambda x: x.sylb == components[i % len(components)])
            child = p_db.first(
                label_c, lambda x: x.sylb == components[floor(i / len(components))]
            )
            relations.append(
                syll_relation(
                    parent.sylb, child.sylb, matrix[i] / colsums[i % len(components)]
                )
            )  # /colsums
            child.freq /= colsums[i % len(components)]
    p_db.add_all(relations,label_r)

    return components, matrix

def main():
    print("main in test_ray\navaliable: {}".format(dir()))
    # general test case
    text = "the quick brown fox jumps over the lazy dog"#.replace(" ", "")
    # more-realistic test case: ALICE'S ADVENTURES IN WONDERLAND by Lewis Carroll
    # TODO: check copyright status for book version/data generated
    text = open("../alice.txt", "r", encoding="utf-8").read()
    #text = open("../foxdog.txt", "r", encoding="utf-8").read()
    chars = list(set(text))
    chars.sort()

    # Insert start & terminating character (not very useful with one sample)
    print("$ in base set: {}".format("$" in chars))
    print("^ in base set: {}".format("^" in chars))
    chars.append("$")
    chars.append("^")

    syllables = [syllabary(c, text.count(c)) for c in chars]
    start_syl = syllables[-1]

    p_db.add_all(syllables)
    # res = p_db.query(syllables[0],lambda slb : slb.sylb == 'a')
    print(p_db.query(syllables[0], lambda slb: slb.sylb == "a"))
    # print("\n".join([i.__repr__() for i in syllables]))
    ptext = "^" + text + "$"
    matrix = [0] * (len(chars) * (len(chars) - 2))
    # printmatrix(chars,matrix)
    for i in range(1, len(text) + 1):
        matrix[getindex(ptext[i - 1], ptext[i], chars)] += 1
        pass
    matrix[getindex("$", text[-1], chars)] += 1
    # probability is count/sum of column
    # matrix=[float('{}{}'.format((i%26==0 or i%27==0)*str(matrix[i]),(i%26!=0 and i%27!=0)*str(matrix[i]/35))) for i in range(0,len(matrix))]
    # printmatrix(chars, matrix)

    relations = []
    colsums = [getcolsum(i, matrix, chars) for i in chars] + [1, 1]
    for i in range(0, len(matrix)):
        if matrix[i]:
            parent = p_db.first(start_syl, lambda x: x.sylb == chars[i % len(chars)])
            child = p_db.first(
                start_syl, lambda x: x.sylb == chars[floor(i / len(chars))]
            )
            relations.append(
                syll_relation(
                    parent.sylb, child.sylb, matrix[i] / colsums[i % len(chars)]
                )
            )  # /colsums
            child.freq /= colsums[i % len(chars)]
    p_db.add_all(relations)
    print("number of syllables", p_db.count(start_syl, lambda x: True))
    print("\n".join([str(i) for i in p_db.query(start_syl, lambda x: True)]))
    print("number of relations", p_db.count(relations[0], lambda x: True))
    print("\n".join([str(i) for i in p_db.query(relations[0], lambda x: True)]))
    #printmatrix(chars, matrix)
    #printmatrix(*matrix_and_count([c for c in text],'text_compare','relation_compare'))  # test for function
    #print("number of syllables", p_db.count('text_compare', lambda x: True))
    #print("\n".join([str(i) for i in p_db.query('relation_compare', lambda x: True)]))

    def make_components(tokens, label_c):
        components = list(set(tokens))
        components.sort()
        components.append("$")
        components.append("^")
        token_obj = [syllabary(c, tokens.count(c)) for c in components]
        p_db.add_all(token_obj, label_c)

        return components

    def make_matrix(components):
        matrix = [0] * (len(components) * (len(components) - 2))
        return matrix

    # now do the same thing for words
    components = make_components(re.findall(r"[a-zA-Z]+", text), "words")
    matrix = make_matrix(components)

    for sentence in re.findall(r"[^.!?]+[.!?]", text):
        print('sentence',sentence)
        textwords = re.findall(r"[a-zA-Z]+", sentence)
        matrix = matrix_and_count([tw for tw in textwords],'words','word_link', components, matrix)[1]
        #printmatrix(components, newmatrix)
        print("\n")
        #matrix = [i+j for i,j in zip(newmatrix, matrix)]
    printmatrix(components, matrix)
    print("number of words", p_db.count('words', lambda x: True))
    print("number of word relations", p_db.count('word_link', lambda x: True))

    # parsing words isn't enough, will need to parse out sentences as well.
    # Each sentence can be used as it's own "source" for a complete thought


if __name__ == "__main__":
    main()

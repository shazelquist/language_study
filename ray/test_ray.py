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
    return sum([matrix[getindex(xchr, i, chars)] for i in chars[:-2]])


def printmatrix(chars, matrix):
    """
    printmatrix(chars, matrix)

    print the matrix with some degree of formatting
    note:
        Formatting not good enough to directly port to csv
    """
    print("\t".join(["N"] + chars))
    # print('{} '.format(chars[0]),end='')
    f_format = '"{}"'  # '{:.1f}'
    ends = "\t"
    colsums = [getcolsum(i, matrix, chars) for i in chars] + [1, 1]
    for i in range(0, len(matrix)):
        if i % len(chars) == 0:
            print(
                '{}"{}"'.format("\n" * (i != 0), chars[floor(i / len(chars))]), end=ends
            )
        if i % len(chars) == len(chars) - 1 or i % len(chars) == len(chars) - 2:
            print(f_format.format(matrix[i]), end=ends)
        elif colsums[i % 28]:
            print(f_format.format(matrix[i] / colsums[i % len(chars)]), end=ends)
        else:
            print(f_format.format(matrix[i]), end=ends)
    print("\n", end="")


def main():
    print("main in test_ray\navaliable: {}".format(dir()))
    # general test case
    text = "the quick brown fox jumps over the lazy dog".replace(" ", "")
    # more-realistic test case: ALICE'S ADVENTURES IN WONDERLAND by Lewis Carroll
    # TODO: check copyright status for book version/data generated
    text = open("../alice.txt", "r", encoding="utf-8").read()
    chars = list(set(text))
    chars.sort()

    p_db.add_all(list(range(0, 10)), "zero to ten")
    print(p_db.cont)
    input()

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

    # now do the same thing for words
    textwords = re.findall(r"[a-zA-Z]+", text)
    word_set = set(textwords)
    words = [syllabary(w, textwords.count(w)) for w in word_set]
    p_db.add_all(words, "words")
    p_db.count("words", lambda x: x.sylb.lower() == "the")
    # print(words)

    # parsing words isn't enough, will need to parse out sentences as well.
    # Each sentence can be used as it's own "source" for a complete thought


if __name__ == "__main__":
    main()

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

    # Insert start & terminating character (not very useful with one sample)
    print("$ in base set: {}".format("$" in chars))
    print("^ in base set: {}".format("^" in chars))
    chars.append("$")
    chars.append("^")

    syllables = [syllabary(c, text.count(c)) for c in chars]
    print("\n".join([i.__repr__() for i in syllables]))
    ptext = "^" + text + "$"
    matrix = [0] * (len(chars) * (len(chars) - 2))
    # printmatrix(chars,matrix)
    for i in range(1, len(text) + 1):
        matrix[getindex(ptext[i - 1], ptext[i], chars)] += 1
        pass
    matrix[getindex("$", text[-1], chars)] += 1
    # probability is count/sum of column
    # matrix=[float('{}{}'.format((i%26==0 or i%27==0)*str(matrix[i]),(i%26!=0 and i%27!=0)*str(matrix[i]/35))) for i in range(0,len(matrix))]
    printmatrix(chars, matrix)


if __name__ == "__main__":
    main()

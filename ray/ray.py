"""
# ray.py
#
# Directive:
#   Provide interface for testing concepts
#   Template for database implementation
#   Probability of syllable progression
"""
# Shane_Hazelquist #Date: Monday, 6/20/2022
# Imports:


class syllabary:
    """
    syllabary

    __init__(sylb, frequency=0)
    Maintains syllable information for calculation and reference
    """

    def __init__(self, sylb, frequency=0):
        """ """
        self.id = id(self)
        self.sylb = sylb
        self.freq = frequency

    def __repr__(self):
        """ """
        return '<{} id={} sylb="{}" freq={}>'.format(
            type(self), self.id, self.sylb, self.freq
        )


class ancestry:
    """
    ancestry

    __init__(parent, child, frequency)

    Given an ancester, keep track of likelyhood of following syllables
    column view of matrix
    needs special terminal cases
    Intended for use in word progressino
    """

    def __init__(self, parent, child, frequency):
        """ """
        self.id = id(self)
        self.syll_parent = parent
        self.syll_child = child
        self.freq = frequency

    def probability(self):
        """ """
        return self.freq / self.syll_parent.freq

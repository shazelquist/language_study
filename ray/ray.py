"""
# ray.py
#
# Directive:
#   Provide interface for testing concepts
#   Template for database implementation
#   Probability of syllable progression
#
#
# Notes:
#   May be better if developed in a oop linked node format.
#   Extending previous order objects will maintain some consistancy
#   Updates to calculations need proper flow because of child dependencies
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

    def update_freq(self, value):
        """ """
        pass

    def probability():
        """ """
        return self.freq/sylabary.sum

    def __repr__(self):
        """ """
        return '<{} id={} sylb="{}" freq={}>'.format(
            type(self), self.id, self.sylb, self.freq
        )


class syll_relation:
    """
    syll_relation

    __init__(parent, child, frequency)

    Given an ancester, keep track of likelyhood of following syllables
    column view of matrix
    needs special terminal cases
    Intended for use in word progression
    """

    def __init__(self, parent, child, frequency):
        """ """
        self.id = id(self)
        self.syll_parent = parent
        self.syll_child = child
        self.freq = frequency

    def update_freq(self, value):
        """ """
        pass

    def probability(self):
        """ """
        self.probability = self.freq / self.syll_parent.freq
        return self.probability

    def __repr__(self):
        """ """
        return "<{} id={} parent_id={} child_id={} freq={}>".format(
            type(self), self.id, self.syll_parent, self.syll_child, self.freq
        )

class higher_relation:
    """
    higher_relation

    __init__(parent_table, parent, child, frequency)

    Given an ancester, keep track of likelyhood of following syllables
    Using parent_table as a reference, we can direct parent queries to higher order
    """

    def __init__(self, parent_table, parent, child, frequency):
        """ """
        self.parent_table
        self.id = id(self)
        self.syll_parent = parent
        self.syll_child = child
        self.freq = frequency

    def probability(self):
        """ """
        self.probability = self.freq / self.syll_parent.freq
        return self.probability

    def update_freq(self, value):
        """ """
        pass

    def __repr__(self):
        """ """
        return "<{} id={} parent_id={} child_id={} freq={}>".format(
            type(self), self.id, self.syll_parent, self.syll_child, self.freq
        )

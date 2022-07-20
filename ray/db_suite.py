#!C:/Python_X64/python
# Shane_Hazelquist #Date: Friday, 7/1/2022  #Time: 12:14.19
# Imports:
from sys import argv
from ray import *
import db_suite as mainself
from json import loads, load

# Directive:
#


def erase_db(param=None):
    if input("Do you really want to delete & remake {}? y/n\t".format(dburl)) != "y":
        return
    print("creating engine")
    engine = create_engine(dburl)
    print("dropping existing")
    Base.metadata.drop_all(engine)
    print("creating all schemea")
    Base.metadata.create_all(engine)
    print("opening session")
    session = Session(engine)


def push_sentence(target, sentence_defi, param=None):

    for sentence in ["source_beg_token"] + re.find_all(sentence_def, target)[
        "source_end_token"
    ]:
        push_relation(target, param)


def push_relation(target, order=1, param=None):

    if order > 1:
        push_relation(target, order - 1, param)
    if order == 1:  # push word instances
        for word in ["sentence_beg_token"] + re.find_all(sentence_def, target)[
            "sentence_end_token"
        ]:
            push_characters(word, param)
    else:  # push relation of given order
        pass


def test_following_plus(param=None):
    input("continue? note, this may mess with data in a current db")
    sents = [
        "the quick brown fox jumped over the lazy dog",
        "the quick red fox jumped over the stinky dog",
        "the ragged fox jumped over the dog",
        "the fox attacked the old dog",
        "a fox attacked an old dog",
        "the old dog could not react to the quick fox",
        "the brown dog could not react to the lazy fox",
    ]
    follows = {}
    autoid = 1
    for sent in sents:
        word_order = sent.split(" ")
        words = [text for text in set(word_order)]
        for w in words:
            label = tuple([w])
            print("word label:", label)
            if label not in follows:
                follows[label] = instance(w, word_order.count(w))
            else:
                follows[label].update_freq(follows[label].freq + word_order.count(w))
            session.add(follows[label])
        # push word changes
        session.commit()
        for i in range(2, len(word_order) + 1):
            j = i
            for s in range(0, len(word_order) + 1):
                if s + i > len(word_order):
                    break
                label = tuple(word_order[s : s + i])
                print("label:", label)
                if label in follows:
                    follows[label].update_freq(follows[label].freq + 1)
                    print("\told object", label, follows[label].id)
                else:
                    # add object:
                    if j == 0:  # follows
                        # parent, text, frequency
                        print("\t\tdegree -", i, len(label[:-1]))
                        follows[
                            label
                        ] = following_plus(  # the -1 offset accounts for the lack of regular following
                            follows[label[:-1]].id,
                            follows[tuple([label[-1]])].id,
                            1,
                            i - 1,
                        )
                    else:  # plus
                        print("\t\tdegree +", i, len(label[:-1]))
                        follows[label] = following_plus(
                            follows[label[:-1]].id,
                            follows[tuple([label[-1]])].id,
                            1,
                            i - 1,
                        )
                    print("\tnew object", label, autoid)
                    follows[label].id = autoid
                    autoid += 1
                j -= 1
    session.add_all([follows[k] for k in follows])
    session.commit()
    print("{} new objects".format(len(follows)))


def following_plus_peek(param=None):
    # modify to use function.func for backtracking
    if not param:
        param = input(
            "Please enter a word from list {}\n: ".format(
                [w.text for w in session.query(instance).all()]
            )
        )
    if " " in param:
        param = param.split(" ")
    else:
        param = [param]
    ids = [
        session.query(instance).filter(instance.text == wrd.lower()).first().id
        for wrd in param
        if wrd
    ]
    # every match for the last word
    # backward matching falls into problems with parent ID
    # Lookup wants forward relation too
    if len(ids) == 1:
        head = (
            session.query(following_plus)
            .filter(
                and_(following_plus.parent_id == ids[-1], following_plus.degree == 1)
            )
            .order_by(following_plus.degree.desc())
            .all()
        )
    elif len(ids) > 1:
        head = (
            session.query(following_plus)
            .filter(
                and_(
                    following_plus.this_id == ids[-1], following_plus.degree < len(ids)
                )
            )
            .order_by(following_plus.degree.desc())
            .all()
        )
    else:
        head = []
    print("given", param, "checking {} canidates".format(len(head)), ids)
    best = []
    rm = []
    validated = []
    if len(param) > 1:
        for h in head:
            node = h
            best.append(len(ids) - 1)
            for i in range(len(ids) - 1, -1, -1):  # reverse iterate from second to last
                id_i = ids[i]
                print(param[i], "against", node.text, i)
                if not hasattr(node, "parent"):  # end of node
                    if node.id == id_i:
                        print("\tpass")
                        validated.append(h)
                        break
                    print("\texiting, failed")
                    rm.append(h)
                    break
                elif hasattr(node, "parent") and node.this_id == id_i:
                    # best[-1] += 1
                    pass  # do nothing and continue
                else:  # this_id did not match
                    print("\tbase did not match", node.this_id, id_i)
                    rm.append(h)
                    break
                    # del best[-1]
                node = node.parent
            if validated:
                break
        head = validated
    for h in head:
        print(
            h.path(),
            "prob {}".format(h.probability),
            [(c.text, c.probability) for c in h.children if len(ids) > 1],
        )


def push_characters(target, param=None):
    pass


def test_data(*param):
    if not param:
        param = input("Please enter a query:")
    for i in param:
        results = (
            session.query(instance)
            .filter(instance.text.startswith(i))
            .order_by(instance.freq)
        )
        if (
            results.count() < 10
            or input(
                '{} results found starting with "{}", show all (y)?'.format(
                    results.count(), i
                )
            )
            == "y"
        ):
            for term in results.all():
                print(term.text, term.freq)


def peek(param=None):
    global session
    print("instances count {}".format(session.query(instance).count()))
    print("following count {}".format(session.query(following).count()))
    print(
        "following freq>1 count {}".format(
            session.query(following).filter(following.freq > 1).count()
        )
    )
    print("following plus {}".format(session.query(following_plus).count()))


def dump_instance(param=None):
    words = session.query(instance).order_by(instance.freq).all()
    print("all instances:")
    for w in words:
        print(w)


def dump_following(param=None):
    words = session.query(following).order_by(following.freq).all()
    print("all following:")
    for w in words[-20:]:
        print(w, w.parent.text, w.text.text)


def guess_next(param=None):
    query = input("enter a word:")
    word = session.query(instance).filter(instance.text == query).first()
    print("word found status:", word)
    if not word:
        return
    options = (
        session.query(following)
        .filter(following.parent_id == word.id)
        .order_by(following.freq)
        .all()
    )
    print("options status", len(options))
    if not options:
        return
    for child in options:
        print(child.text.text, child.probability)


def echo(*param):
    print(param)


def load_dictionary(source=temp_path + "terms.json", param=None):
    with open(source, "r", encoding="utf-8") as jfile:
        dic_terms = load(jfile)
    existing = [inst.text for inst in session.query(instance).all()]
    print("comparing new objects to existing")
    new_terms = [
        instance(term, 0) for term in dic_terms if term not in existing
    ]  # load as obj
    print("{} new terms to push".format(len(new_terms)))
    session.add_all(new_terms)
    session.commit()


def test_dictionary():
    print("loading terms")
    terms = loads(open(temp_path + "terms.json", "r", encoding="utf-8").read())
    print("comparing db against terms")
    missing = [t.text for t in session.query(instance).all() if t.text not in terms]
    print(missing)
    print("{} terms missing".format(len(missing)))


def main():
    cm_param = argv[1:]
    print("starting suite, param:", cm_param)
    actions = [i[1:] for i in cm_param if (i and i[0] == "-")]
    print("starting actions", actions)
    print("avaliable actions:", dir(mainself))
    while actions:
        print(actions)
        action = actions[0]
        plimit = cm_param.index("-" + action) + 1
        while plimit < len(cm_param) and cm_param[plimit][0] != "-":
            plimit += 1
        print(cm_param[cm_param.index("-" + action) + 1 : plimit])

        if action in dir(mainself):
            print('found function "{}"'.format(action))
            getattr(mainself, action)(
                *cm_param[cm_param.index("-" + action) + 1 : plimit]
            )
        else:
            print('could not find function "{}"'.format(action))

        del actions[0]
        del cm_param[:plimit]

    for aindex in range(0, len(actions)):
        action = actions[aindex]
        pstart = cm_param.index("-" + action)
        plimit = len(cm_param)
        if aindex < len(actions):
            plimit = cm_param.index("-" + actions[aindex + 1])
        print("splice [{}:{}]".format(pstart, plimit), cm_param[pstart:plimit])
        # index = cm_param.index('-'+action)


if __name__ == "__main__":
    main()

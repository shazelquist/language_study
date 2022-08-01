#!C:/Python_X64/python
# Shane_Hazelquist #Date: Friday, 7/1/2022  #Time: 12:14.19
# Imports:
from sys import argv
from ray import *
import db_suite as mainself
from json import loads, load, dump
from sqlalchemy import update
from sqlalchemy.orm import aliased
from collections import Counter  # todo

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


def delay_ops(dset, dqueue):
    dq = []
    print(dset)
    for k in dqueue:
        dq.append([k, dqueue[k]])
    with open(temp_path + "delayed_set.json", "w", encoding="utf-8") as wordset:
        dump(list(dset), wordset)
    with open(temp_path + "delayed_ops.json", "w", encoding="utf-8") as delay:
        # print(dq)
        dump(dq, delay)


def verify_words(param=None):
    with open(temp_path + "delayed_set.json", "r", encoding="utf-8") as wordset:
        objects = load(wordset)
    with open(temp_path + "delayed_set.json", "w", encoding="utf-8") as wordset:
        wordset.write("[]")
    for ob in objects:
        print(ob)
        # may have conflicts
        session.add(instance(ob, 0))
    with open(temp_path + "delayed_ops.json", "r", encoding="utf-8") as delay:
        objects = load(delay)
    # print(objects)
    session.commit()


def update_instance(sentences, follows):
    words = Counter()
    for s in sentences:
        for w in s:
            print("ui:", w)
            words[w] += 1
    delayset = set()
    for w in words:
        if (w,) in follows:
            follows[(w,)].add_freq(words[w])
        else:
            delayset.update([w])
    return delayset


def test_following_plus(param=None, validated_delay=[], maxdeg=0):
    """
    Test following plus by loading sentence information

    Act as a debug system to investigate normal loading routines
    \p{Han}\p{Hiragana}\p{Katakana}
    General plan:
        -requires sentences and any validated_delay
        -sentences are lists of words in the order that they should appear, in lower case if ENG
        -validated delay are work items from previously delayed runs (where instance could not be found)

        -preload instances to follows cache
        -calculate degrees based on sentence lengths
        -for each degree:
            update value if in cache, or:
            generate a work_order from the sentence tuples of the length of our degree

            check cache for parent.id and this.id dependencies and add to push order if exists
            or delayqueue the request

    """
    input("continue? note, this may mess with data in a current db")
    sentences = [
        "the quick brown fox jumped over the lazy dog",
        "the quick red fox jumped over the stinky dog",
        "the ragged fox jumped over the dog",
        "the fox attacked the old dog",
        "a fox attacked an old dog",
        "the old dog could not react to the quick fox",
        "the brown dog could not react to the lazy fox",
    ]
    # sentences = open('../clean_alice.txt','r',encoding='utf-8').read().split('\n')
    sentences = [sent.split(" ") for sent in sentences]
    follows = (
        {}
    )  # TODO: notice, follows cache only needs instances and the last di's results. Smaller cache faster hits
    max_follow = None
    telemetry = Counter()
    # Given source, check current source in the database

    # Add this current source to the database

    # preload follows with existing database information
    # The problem with preloads is it requires lots of work for small additions, should work on merge version instead
    for wrd in session.query(instance).all():
        follows[wrd.path()] = wrd
    print("instance preload-complete")
    delayset = update_instance(sentences, follows)
    print("instance update-complete, {} not found".format(len(delayset)))

    # for flw in session.query(following_plus).all():
    #    follows[flw.path()] = flw

    # Pull the max id from the database to insert as autoid
    autoid = max([i[0] for i in session.query(following_plus.id).all()] + [1])
    print("autoid", end=":")
    print(autoid)

    maxdeg = max([len(sent) for sent in sentences] + [maxdeg])
    degrees = range(2, maxdeg)
    delayqueue = Counter()

    for di in degrees:
        work_order = (
            [] + validated_delay
        )  # TODO: validated_delay is empty but should be loadable from temp/delayed_ops.json (method prob req)
        updated_obj = []
        # generate all the tuples of length di and save in work_order
        for word_order in sentences:
            for s in range(0, len(word_order) + 1):
                if s + di > len(word_order):
                    break
                label = tuple(word_order[s : s + di])
                if label in follows:  # early cache check
                    telemetry["early_cache"] += 1
                    follows[label].add_freq()
                    updated_obj.append(follows[label])
                else:
                    work_order.append(
                        (
                            label[:-1],
                            label,
                        )
                    )
        di -= 1  # TODO notice, degree is off by one in objects

        # prnt_obj = session.query(following_plus.parent_id,following_plus).filter(following_plus.degree==di-1).filter(following_plus.this_id.in_(work_order['this_id'])).order_by(following_plus.parent_id).order_by(following_plus.this_id).all()
        # update work_obj
        push_order = Counter()
        for order in work_order:
            # this:
            # if not early cache check, do here
            # check follows cache for this:ids, parent:ids
            # new word, delay
            if (order[1][-1],) in follows and order[0] in follows:
                # print('{}:{}'.format(order[0],follows[order[0]].id))
                telemetry["push_order"] += 1
                push_order[
                    (
                        follows[order[0]].id,
                        follows[(order[1][-1],)].id,
                        order[1],
                    )
                ] += 1
            else:
                # this_word or parent is not in cache
                # print('delayqueue:{}'.format(order))
                telemetry["delay_queue"] += 1
                delayqueue[order] += 1

        print("query work_obj...")
        work_obj = (
            session.query(following_plus.parent_id, following_plus.id, following_plus)
            .filter(following_plus.degree == di)
            .filter(following_plus.this_id.in_([i[1] for i in push_order]))
            .order_by(following_plus.parent_id)
            .all()
        )
        print("query work_obj done")

        print(len(work_obj), "work objects")
        print("mem_check for push objects")
        # pushorder: (parent_label, thislabel)
        for po in push_order:
            pobject = [w for w in work_obj if w[0] == po[0] and w[1] == po[1]]
            if pobject:
                telemetry["DB_hit"] += 1
                # print('DB hit',push_order[po],po)
                # input('pobject: {}'.format(pobject[0][2]))
                pobject[0][2].add_freq(push_order[po])
                updated_obj.append(pobject[0][2])
                work_obj.remove(pobject[0])
                # push_order.popitem(po)
            else:
                # print('new object needed', po[0],po[1],push_order[po])
                telemetry["DB_miss_create_new"] += 1
                newobj = following_plus(po[0], po[1], push_order[po], di)
                # print('\t',po[2],newobj)
                follows[po[2]] = newobj
                updated_obj.append(newobj)

        print(
            "{} in delay queue, {} rdy to commit, {} to merge check di {}".format(
                len(delayqueue), len(updated_obj), len(push_order), di
            )
        )
        session.add_all(updated_obj)
        session.commit()
    print(
        "\n{} new objects in delayqueue\nDELAYSET:{}".format(len(delayqueue), delayset)
    )

    delay_ops(delayset, delayqueue)
    print("for {} sentences:".format(len(sentences)), telemetry)
    if delayset:
        print('please run "verify_words" and then this again')


def following_plus_peek(param=None):
    # modify to use function.func for backtracking
    if not param:
        param = input(
            "Please enter a word from list {}\n: ".format(
                ["too much data"]  # [w.text for w in session.query(instance).all()]
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
                # print(param[i], "against", node.text, i)
                if not hasattr(node, "parent"):  # end of node
                    if node.id == id_i:
                        print("\tpass")
                        validated.append(h)
                        break
                    # print("\texiting, failed")
                    rm.append(h)
                    break
                elif hasattr(node, "parent") and node.this_id == id_i:
                    # best[-1] += 1
                    pass  # do nothing and continue
                else:  # this_id did not match
                    # print("\tbase did not match", node.this_id, id_i)
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


def sources(*param):
    opts = []
    if param:
        opts = param
    if "maketag" in opts:
        session.add(tag("debug"))
        session.add(tag("dictionary"))
        session.add(tag("text"))
        session.add(tag("web"))
        session.add(tag("book"))
        session.commit()
    if "showtag" in opts:
        print(list(session.query(tag).all()))
    if "showass" in param:
        for association in session.query(model_source_tags):
            print(association)
    if "makesource" in opts:
        db_alice = model_source("debug_alice.txt", "fake_textfile")
        session.add(db_alice)
        session.commit()
        db_alice.add_tags(["debug", "text"]).commit()
    if "showsource" in opts:
        print((session.query(model_source).all()))


def debug(param=None):
    print(session.query(instance).filter(instance.id == 9).all())  # 9,15,19
    print(session.query(instance).filter(instance.id == 15).all())  # 9,15,19
    print(session.query(instance).filter(instance.id == 19).all())  # 9,15,19
    text = input("\ngive me a word: ")
    print('looking for "{}"'.format(text))
    ires = session.query(instance).filter(instance.text == text).first()
    print(ires, session.query(instance).filter(instance.text == text).count())
    fps = session.query(following_plus).filter(following_plus.this_id == ires.id).all()
    print("next\n")
    for fp in fps:
        print(fp, fp.path(), fp.parent)


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


def clean_alice():
    """
    Known issues:
    - Chapter titles, spacing defined seperation
    - numbers
    - block/quotes cut off
    """
    import re

    def any(tup):
        if tup[0]:
            return tup[0].lower()
        elif tup[1]:
            return tup[1].lower()

    text = open("../alice.txt", "r", encoding="utf-8").read()
    out = open("../clean_alice.txt", "w", encoding="utf-8")
    for sentence in re.findall(r"[^.!?]+[.!?]", text):
        if sentence:
            sentence = sentence.replace("\n", " ")
            words = [
                any(i)
                for i in re.findall(
                    r"([a-zA-Z]+[\-\'][a-zA-Z]+)|([&a-zA-Z]+)", sentence
                )
                if i
            ]
            out.write(" ".join(words) + "\n")
    out.close()
    print("done")


def main():
    cm_param = argv[1:]
    print("starting suite, param:", cm_param)
    actions = [i[1:] for i in cm_param if (i and i[0] == "-")]
    print("starting actions", actions)
    print("avaliable actions:", [i for i in dir(mainself) if "__" not in i])
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

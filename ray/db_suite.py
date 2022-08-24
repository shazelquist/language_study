#!/usr/bin/python3
#!C:/Python_X64/python
# -*- coding = utf-8 -*-
# Shane_Hazelquist #Date: Friday, 7/1/2022  #Time: 12:14.19
# Imports:
from sys import argv
from os import listdir
from datetime import datetime
import suite
from ray import *
import db_suite as mainself
from json import loads, load, dump
from sqlalchemy import update, or_, tuple_
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import func
from collections import Counter  # todo

# Directive:
#


@suite.add_func
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


def serialize_delayset(dset):
    with open(temp_path + "delayed_set.json", "w", encoding="utf-8") as wordset:
        dump(list(dset), wordset)


def serialize_delayqueue(dqueue):
    with open(temp_path + "delayed_ops.json", "w", encoding="utf-8") as wordset:
        for k in dequeue:
            dqueue[k] = dict(dqueue[k])
        dump(dqueue, wordset)

@suite.add_func
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


@suite.add_func
def update_instance(sentences, follows, add=True):
    words = Counter()
    for s in sentences:
        for w in s:
            words[w] += 1
    delayset = set()
    ui = {}
    for w in words:
        if (w,) in follows:
            follows[(w,)].add_freq(words[w])
            ui[(w,)] = follows[(w,)]
            if add:
                session.add(follows[(w,)])
        else:
            delayset.update([w])
    print("updated instance of {} words".format(len(words)))
    return delayset, ui


def make_sentences(text):
    sentences = [[wrd for wrd in sent.split(" ") if wrd] for sent in text.split("\n")]
    return sentences


@suite.add_func
def push_book(title=None):
    if title:
        clean_name = "clean_" + title + ".txt"
        print('checking for "{}"'.format(title))
        if (
            session.query(model_source)
            .filter(model_source.specific == clean_name)
            .first()
        ):
            print("Book already added")
            exit(1)
        text = open("../books/" + clean_name, "r", encoding="utf-8").read()
        sentences = make_sentences(text)
        print("\nParse {} sentences? y/n".format(len(sentences)))
        commit_status = False
        if input("Confirm commit status: ") == "y":
            commit_status = True
        test_following_plus(sentences, commit_status=commit_status)
        if commit_status:
            print('pushing book "{}" as source'.format(title))
            ref = model_source(title, clean_name)
            session.add(ref)
            session.commit()
            ref.add_tag("book")
            session.commit()
    else:
        print(
            "Books avaliable:\n\t{}".format(
                "\n\t".join([bk[6:] for bk in listdir("../books") if "clean_" in bk])
            )
        )


def test_following_plus(
    sentences=None, validated_delay={}, maxdeg=0, commit_status=False
):
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

    if commit_status:
        print("commit warning")
        input("continue? note, this may mess with data in a current db")
    print()
    if not sentences:
        sentences = [
            "the quick brown fox jumped over the lazy dog",
            "the quick red fox jumped over the stinky dog",
            "the ragged fox jumped over the dog",
            "the fox attacked the old dog",
            "a fox attacked an old dog",
            "the old dog could not react to the quick fox",
            "the brown dog could not react to the lazy fox",
        ]
    # maxdeg = 5
    # title = "The_Picture_of_Dorian_Gray"

    start_time = datetime.now()
    follows_i = (
        {}
    )  # TODO: notice, follows cache only needs instances and the last di's results. Smaller cache faster hits
    max_follow = None
    telemetry = Counter()
    # Given source, check current source in the database

    # Add this current source to the database

    # preload follows with existing database information
    # The problem with preloads is it requires lots of work for small additions, should work on merge version instead
    for wrd in session.query(instance).all():
        follows_i[wrd.path()] = wrd
    print("instance preload-complete")
    delayset, follows_i = update_instance(
        sentences, follows_i, add=False
    )  # add contributes to database freq TODO
    serialize_delayset(delayset)
    if delayset:
        print(
            'please check "{}delayed_set.json" to verify then run "verify_words" and then this again'.format(
                temp_path
            )
        )
        exit(1)
    print("instance update-complete, {} not found".format(len(delayset)))

    if not maxdeg or maxdeg < 2:
        maxdeg = max([len(sent) for sent in sentences] + [0])
    degrees = range(2, maxdeg)
    delayqueue_dic = {}
    follows_l = {}

    if degrees:
        print("Begining parse to degree {}".format(degrees[-1]))
    for di in degrees:
        delayqueue = Counter()
        # set follows cache with the last and inistances
        follows = {}
        follows.update(follows_i)
        follows.update(follows_l)
        follows_l = {}
        if di in validated_delay:
            work_order = [] + validated_delay[di]
        else:
            work_order = (
                []
            )  # TODO: validated_delay is empty but should be loadable from temp/delayed_ops.json (method prob req)
        updated_obj = []
        # generate all the tuples of length di and save in work_order
        wo_i = 0
        while wo_i < len(
            sentences
        ):  # use copy for iterable, this is hard on mem, should work otherwise TODO notice, recently untracked modification to swap to a while loop instead of for with iterator
            # for word_order in sentences:
            word_order = sentences[wo_i]
            inc = 1
            if di > len(word_order):
                sentences.pop(wo_i)
                telemetry["degree_removal"] += 1
                inc = 0
                continue
            for s in range(0, len(word_order) + 1):
                if s + di > len(word_order):
                    break
                label = tuple(word_order[s : s + di])
                work_order.append(
                    (
                        label[:-1],
                        label,
                    )
                )
            wo_i += inc
        di -= 1  # TODO notice, degree is off by one in objects

        # update work_obj
        push_order = Counter()
        if di in validated_delay:
            push_order = Counter(validated_delay[di])
        for order in work_order:
            # this:
            # if not early cache check, do here
            # check follows cache for this:ids, parent:ids
            # new word, delay
            if (order[1][-1],) in follows and order[0] in follows:
                telemetry["push_order"] += 1
                push_order[
                    (
                        follows[order[0]].id,
                        follows[(order[1][-1],)].id,
                        order[1],
                    )
                ] += 1
                # print('new push order: {} : {} :{}'.format(follows[order[0]].id, follows[(order[1][-1],)].id,order[1]))
            else:
                # this_word or parent is not in cache
                print("delayqueue:{}".format(order))
                telemetry["delay_queue"] += 1
                delayqueue[order] += 1
                if (order[1][-1],) not in follows:
                    telemetry["missing_this_id"] += 1
                else:
                    telemetry["missing_parent_id"] += 1

        print("query work_obj...")
        # TODO: Large push orders will cause errors by excceding the "in_" clause limit 29k is fine, 47k is not
        work_obj = []
        print(
            "pushorder size {} di {} follows {}".format(
                len(push_order), di, len(follows)
            )
        )
        # input('cont?')
        work_obj = []
        ref_obj = []

        po_combo = [(pi[0], pi[1]) for pi in push_order]

        # print(dir(session.query(following_plus)))
        print("start new query")
        logit = datetime.now()

        work_obj = []
        ref_obj = []
        # rough estimate of 15000 portions before hitting object limit
        if po_combo:
            blocks = list(range(0, len(push_order), 15000)) + [len(push_order)]
            for bi in range(0, len(blocks) - 1):
                po_slice = po_combo[blocks[bi] : blocks[bi + 1]]  # limit in_ size
                work_obj += (
                    session.query(following_plus)
                    .filter(following_plus.degree == di)
                    .filter(
                        tuple_(following_plus.parent_id, following_plus.this_id).in_(
                            po_slice
                        )
                    )
                    .all()
                )
                ref_obj += (
                    session.query(following_plus)
                    .filter(following_plus.degree == di)
                    .filter(
                        tuple_(following_plus.parent_id, following_plus.this_id).in_(
                            po_slice
                        )
                    )
                    .with_entities(following_plus.parent_id, following_plus.this_id)
                    .all()
                )
        print(
            "given results {}, {} at :{}".format(
                len(work_obj), len(ref_obj), datetime.now() - logit
            )
        )
        # print('\n'.join([str(wi.path()) for wi in work_obj]))

        # if len(push_order) != len(work_obj):
        #    print("\n\nERROR, could not find everything")
        #    input("continue?")

        print(len(work_obj), "work objects")
        print("mem_check for {} push objects".format(len(push_order)))
        # pushorder: (parent_label, thislabel)
        for po in push_order:  # majority of computation time
            # list against list
            if po[:-1] in ref_obj:
                pobject = work_obj[ref_obj.index(po[:-1])]
                telemetry["DB_hit"] += 1
                # print('DB hit',push_order[po],po)
                # input('pobject: {}'.format(pobject[0][2]))
                pobject.add_freq(push_order[po])
                updated_obj.append(pobject)
                # follows[po[2]] = pobject
                follows_l[po[2]] = pobject
                work_obj.remove(pobject)  # limit size
                ref_obj.remove(po[:-1])  # limit size
                # push_order.popitem(po)
            else:
                # print('new object needed', po[0],po[1],push_order[po])
                telemetry["DB_miss_create_new"] += 1
                newobj = following_plus(po[0], po[1], push_order[po], di)
                # print('\t',po[2],newobj)
                # follows[po[2]] = newobj
                follows_l[po[2]] = newobj
                updated_obj.append(newobj)
            # input('quit')
        print(
            "\n{} in delay queue, {} rdy to commit, {} to merge check di {}".format(
                len(delayqueue), len(updated_obj), len(push_order), di
            )
        )
        if delayqueue:
            delayqueue_dic[di] = delayqueue
        session.add_all(updated_obj)
        if commit_status:
            session.commit()

    print(
        "\n{} new objects in delayqueue\nDELAYSET:{}".format(len(delayqueue), delayset)
    )

    print("for {} sentences:".format(len(sentences)), telemetry)
    if delayqueue_dic:
        print("{} degrees in delayqueue_dic".format(len(delayqueue_dic)))
        serialize_delayqueue(delayqueue_dic)
    print(
        "Completed in {}, commit status:{}".format(
            datetime.now() - start_time, commit_status
        )
    )


@suite.add_func
def check_instance(*param):
    if not param:
        param = input("please enter a word to check: ")
    else:
        param = param[0]
    res = session.query(instance).filter(instance.text == param).first()
    multi = session.query(instance).filter(instance.text.startswith(param)).all()
    if not res:
        print('"{}" did not appear'.format(param))
        if multi:
            print("\ndid you mean...")
            for mul in multi:
                print("\t{}".format(mul))
    else:
        print(res)
        print("{} multi's found".format(len(multi)))


@suite.add_func
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


@suite.add_func
def add_tag(*param):
    print('add "{}" as a new tag? y/n'.format(param))
    if input("confirm: ") == "y":
        session.add(tag(param))
        session.commit()
        print("Done")


@suite.add_func
def sources(*param):
    opts = []
    if param:
        opts = param
    if "maketag" in opts:
        # session.add(tag("debug"))
        # session.add(tag("dictionary"))
        # session.add(tag("text"))
        # session.add(tag("web"))
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
        for source in session.query(model_source).all():
            print(source)


@suite.add_func
def debug(param=None):
    fp1 = aliased(following_plus)
    fp2 = aliased(following_plus)
    fp3 = aliased(following_plus)
    print("1 {}, 2 {}, 3 {}".format(fp1, fp2, fp3))
    print("obj", dir(fp1))
    print("query", dir(session.query(fp1)))
    r1 = session.query(fp1).filter(fp1.degree == 2)
    r2 = session.query(fp2).filter(fp2.this_id.in_(list(range(1, 10000))))
    r3 = session.query(fp3).filter(fp3.parent_id.in_(list(range(100, 10000))))
    print(r1.intersect(r2, r3).count())
    # print(r1.join(r2).first())
    # res = session.query(fp2).join(fp1, fp2.id==fp1.id).filter(fp2.id>2).filter(fp1.id<10).order_by(fp1.id.desc()).
    # print(res)


@suite.add_func
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


@suite.add_func
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


@suite.add_func
def dump_instance(param=None):
    words = session.query(instance).order_by(instance.freq).all()
    print("all instances:")
    for w in words:
        print(w)


@suite.add_func
def dump_following(param=None):
    words = session.query(following).order_by(following.freq).all()
    print("all following:")
    for w in words[-20:]:
        print(w, w.parent.text, w.text.text)


@suite.add_func
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


@suite.add_func
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


@suite.add_func
def test_dictionary():
    print("loading terms")
    terms = loads(open(temp_path + "terms.json", "r", encoding="utf-8").read())
    print("comparing db against terms")
    missing = [t.text for t in session.query(instance).all() if t.text not in terms]
    print(missing)
    print("{} terms missing".format(len(missing)))


@suite.add_func
def clean_book(title):
    """
    Known issues:
    - Chapter titles, spacing defined seperation
    - numbers
    - block/quotes cut off
    """
    import re

    # title = 'alice'
    # title = 'Pride_and_Prejudice'
    def any(tup):
        if tup[0]:
            return tup[0].lower()
        elif tup[1]:
            return tup[1].lower()

    text = open("../books/" + title + ".txt", "r", encoding="utf-8").read()
    out = open("../books/clean_" + title + ".txt", "w", encoding="utf-8")
    lines = 0
    if text:
        print('"{}" book found'.format(title))
    for sentence in re.findall(r"[^.!?]+[.!?]", text):
        if sentence:
            sentence = sentence.replace("\n", " ")
            words = [
                any(i)
                for i in re.findall(
                    r"([a-zA-Z]+[\-\'\’][a-zA-Z]+)|([&a-zA-Z]+)", sentence
                )
                if i and len(i) > 0
            ]
            if words:
                out.write(" ".join(words) + "\n")
                lines += 1
    out.close()
    print("done, wrote {} lines".format(lines))


def main():
    suite.run_suite()

if __name__ == "__main__":
    main()

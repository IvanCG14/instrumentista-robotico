import os

import yaml

from surgical_assistant.nlu import NLU, normalize

CFG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'instruments.yaml')


def make_nlu():
    with open(CFG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    return NLU(cfg['instruments'])


def test_normalize():
    assert normalize('¡Pásame el Bisturí, por favor!') == 'pasame el bisturi por favor'


def test_give_scalpel():
    r = make_nlu().parse('Pásame el bisturí')
    assert (r.intent, r.instrument) == ('give_instrument', 'scalpel')
    assert r.confidence >= 0.6


def test_longest_alias_wins():
    r = make_nlu().parse('dame la pinza hemostática')
    assert r.instrument == 'hemostat'
    r = make_nlu().parse('dame la pinza')
    assert r.instrument == 'forceps'


def test_other_instruments():
    n = make_nlu()
    assert n.parse('necesito las tijeras').instrument == 'scissors'
    assert n.parse('alcánzame el porta agujas').instrument == 'needle_holder'
    assert n.parse('traeme el portaagujas').instrument == 'needle_holder'


def test_fuzzy_asr_error():
    r = make_nlu().parse('pasame el bisturri')
    assert r.instrument == 'scalpel' and r.intent == 'give_instrument'


def test_stop_variants_and_ambiguous_para():
    n = make_nlu()
    assert n.parse('alto').intent == 'stop'
    assert n.parse('para').intent == 'stop'
    assert n.parse('detente ahora mismo').intent == 'stop'
    # "para" dentro de una frase larga NO es stop
    assert n.parse('pásame el bisturí para la incisión').intent == 'give_instrument'


def test_stop_beats_everything():
    r = make_nlu().parse('alto no me pases el bisturí')
    assert r.intent == 'stop' and r.instrument == ''


def test_home_and_return():
    n = make_nlu()
    assert n.parse('vuelve a la posición inicial').intent == 'home'
    r = n.parse('toma el bisturí')
    assert (r.intent, r.instrument) == ('return_instrument', 'scalpel')


def test_unknown_and_missing_instrument():
    n = make_nlu()
    assert n.parse('buenos días doctor').intent == 'unknown'
    r = n.parse('pásame eso')
    assert r.intent == 'give_instrument' and r.instrument == '' and r.confidence <= 0.3

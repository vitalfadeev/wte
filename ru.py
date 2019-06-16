# !/usr/bin/python3
# -*- coding: utf-8 -*-

from wte import KEYS, WORD_TYPES
from wte import WORD_TYPES as wt
from wikoo import Li, Template, Section, Link, String
from loggers import log, log_non_english, log_no_words, log_unsupported
from loggers import log_uncatched_template, log_lang_section_not_found, log_tos_section_not_found
from helpers import merge_two_dicts, check_flag
import miners
from miners import \
    if_any, \
    has_flag_in_name, has_flag_in_explaination, has_flag_in_text, \
    has_section, has_template, has_template_with_flag, \
    has_arg, has_flag, has_value, has_arg_and_value_contain, has_arg_with_flag_in_name, \
    has_flag_in_text_recursive, \
    find_terms, \
    get_label_type, find_explainations, \
    term0_cb, term1_cb, lang0_term1_cb, lang0_term2_cb, t_plus_cb, w_cb, alter_cb, en_conj_cb, \
    find_all, find_any, \
    in_section, in_template, in_arg, in_arg_with_flag_in_value, in_link, in_t_plus, in_callback


LANGUAGES = [ "ru", "русский", '-cyrl-' ]
LANG_SECTIONS = [ "ru", "-ru-", "русский", '-cyrl-', "-mwl-" ] # "translingual"
TYPE_OF_SPEECH = {
    wt.NOUN          : ['существительное', 'существительные', '(существительное)', '(существительные)', 'inflection сущ ru', 'inflection сущ ru/text', 'сущ ru', 'сущ ru  m a 1a', 'сущ ru  m ina 1a', 'сущ ru  m ina 6a', 'сущ ru f a', 'сущ ru f a (п 1a)', 'сущ ru f a (п 1b)', 'сущ ru f a (п 2а)', 'сущ ru f a (п 3a)', 'сущ ru f a (п 4a)', 'сущ ru f a 0', 'сущ ru f a 1*a', 'сущ ru f a 1*b', 'сущ ru f a 1*d', 'сущ ru f a 1a', 'сущ ru f a 1b', 'сущ ru f a 1b?', 'сущ ru f a 1d', 'сущ ru f a 1f', 'сущ ru f a 2*a', 'сущ ru f a 2*a(2)', 'сущ ru f a 2*a^', 'сущ ru f a 2*b', 'сущ ru f a 2a', 'сущ ru f a 2a(2)', 'сущ ru f a 2b', 'сущ ru f a 2c^', 'сущ ru f a 3*a', 'сущ ru f a 3*b', 'сущ ru f a 3a', 'сущ ru f a 3b', 'сущ ru f a 3b?', 'сущ ru f a 3d', 'сущ ru f a 3f', 'сущ ru f a 4a', 'сущ ru f a 4a(2)', 'сущ ru f a 4b', 'сущ ru f a 4b^', 'сущ ru f a 5*d^', 'сущ ru f a 5a', 'сущ ru f a 5a^', 'сущ ru f a 5b', 'сущ ru f a 6*a', 'сущ ru f a 6*b', 'сущ ru f a 6*d^', 'сущ ru f a 6a', 'сущ ru f a 6a^', 'сущ ru f a 6a÷', 'сущ ru f a 6b', 'сущ ru f a 6d', 'сущ ru f a 7a', 'сущ ru f a 7b', "сущ ru f a 8*b'-ш", 'сущ ru f a 8a', 'сущ ru f a 8e', 'сущ ru f a 8e-ш', 'сущ ru f a 8e^', "сущ ru f a 8e^'", 'сущ ru f ina', 'сущ ru f ina  (п 1a)', 'сущ ru f ina  1a', 'сущ ru f ina  8a', 'сущ ru f ina (1?)', 'сущ ru f ina (1a)', 'сущ ru f ina (1a^)', 'сущ ru f ina (3*a)', 'сущ ru f ina (3a)', 'сущ ru f ina (мс 6*b)', 'сущ ru f ina (п 1a)', 'сущ ru f ina (п 1b)', 'сущ ru f ina (п 2a)', 'сущ ru f ina (п 3a)', 'сущ ru f ina (п 3b)', 'сущ ru f ina (п 4a)', 'сущ ru f ina 0', 'сущ ru f ina 1*a', 'сущ ru f ina 1*b', 'сущ ru f ina 1*b^', 'сущ ru f ina 1*d', 'сущ ru f ina 1*e', 'сущ ru f ina 1*f', 'сущ ru f ina 1a', 'сущ ru f ina 1a^', 'сущ ru f ina 1b', 'сущ ru f ina 1b?', 'сущ ru f ina 1b÷', 'сущ ru f ina 1d', "сущ ru f ina 1d'", 'сущ ru f ina 1d-', 'сущ ru f ina 1e', 'сущ ru f ina 1f', "сущ ru f ina 1f'", 'сущ ru f ina 2*a', 'сущ ru f ina 2*a(2)', 'сущ ru f ina 2*a-ня', 'сущ ru f ina 2*a-ня(2)', 'сущ ru f ina 2*a^', 'сущ ru f ina 2*b', 'сущ ru f ina 2*b^', 'сущ ru f ina 2*d', "сущ ru f ina 2*d'", 'сущ ru f ina 2*e^', 'сущ ru f ina 2a', 'сущ ru f ina 2a(2)', 'сущ ru f ina 2b', 'сущ ru f ina 2d', "сущ ru f ina 2d'", 'сущ ru f ina 2e', 'сущ ru f ina 2f', 'сущ ru f ina 2f(2)', 'сущ ru f ina 3*a', 'сущ ru f ina 3*b', 'сущ ru f ina 3*b^', 'сущ ru f ina 3*d', 'сущ ru f ina 3*d^', 'сущ ru f ina 3*e', 'сущ ru f ina 3*f', "сущ ru f ina 3*f'", 'сущ ru f ina 3a', 'сущ ru f ina 3b', 'сущ ru f ina 3b?', 'сущ ru f ina 3b÷', 'сущ ru f ina 3d', "сущ ru f ina 3d'", 'сущ ru f ina 3f', "сущ ru f ina 3f'", 'сущ ru f ina 4a', 'сущ ru f ina 4a(2)', 'сущ ru f ina 4b', 'сущ ru f ina 4d', "сущ ru f ina 4d'", 'сущ ru f ina 4f', 'сущ ru f ina 5*a', 'сущ ru f ina 5*b', 'сущ ru f ina 5a', 'сущ ru f ina 5b', 'сущ ru f ina 6*a', 'сущ ru f ina 6*b', 'сущ ru f ina 6*b^', 'сущ ru f ina 6*d^', 'сущ ru f ina 6a', 'сущ ru f ina 6a^', 'сущ ru f ina 6b', 'сущ ru f ina 6d', 'сущ ru f ina 7a', 'сущ ru f ina 7b', 'сущ ru f ina 7b^', "сущ ru f ina 8*b'", "сущ ru f ina 8*b'ш", 'сущ ru f ina 8*e^', 'сущ ru f ina 8a', 'сущ ru f ina 8a-ш', 'сущ ru f ina 8a^', 'сущ ru f ina 8e', 'сущ ru f ina 8e-ш', 'сущ ru f ina 8e^', "сущ ru f ina 8e^'", 'сущ ru f ina 8f"', 'сущ ru f ina 8f"-ш', 'сущ ru ina', 'сущ ru ina pt 0', 'сущ ru m 0', 'сущ ru m a', 'сущ ru m a (n 3*a(1))', 'сущ ru m a (n a 3*b(1)(2))', 'сущ ru m a (мс 1a)', 'сущ ru m a (п 1a)', 'сущ ru m a (п 1b)', 'сущ ru m a (п 3a)', 'сущ ru m a (п 4a)', 'сущ ru m a (с3a(1))', 'сущ ru m a (с4а(1))', 'сущ ru m a 0', 'сущ ru m a 1*a', 'сущ ru m a 1*b', 'сущ ru m a 1a', 'сущ ru m a 1a((2))', 'сущ ru m a 1a(2)', 'сущ ru m a 1a(2)^', 'сущ ru m a 1a^', 'сущ ru m a 1a^-ь', 'сущ ru m a 1b', 'сущ ru m a 1b(1)', 'сущ ru m a 1b^', 'сущ ru m a 1c', 'сущ ru m a 1c(1)', 'сущ ru m a 1c^', 'сущ ru m a 1e', 'сущ ru m a 1e^', 'сущ ru m a 1°a', 'сущ ru m a 1°a^', 'сущ ru m a 1°a^-а', 'сущ ru m a 1°c(1)', 'сущ ru m a 2*a', 'сущ ru m a 2*b', 'сущ ru m a 2*e', 'сущ ru m a 2a', 'сущ ru m a 2a^', 'сущ ru m a 2b', 'сущ ru m a 2c(1)', 'сущ ru m a 2c^', 'сущ ru m a 2e', 'сущ ru m a 2f', 'сущ ru m a 3*a', 'сущ ru m a 3*a(2)', 'сущ ru m a 3*b', 'сущ ru m a 3*c', 'сущ ru m a 3a', 'сущ ru m a 3b', 'сущ ru m a 3c^', 'сущ ru m a 3d', 'сущ ru m a 3e', 'сущ ru m a 3°a', 'сущ ru m a 3°a"', "сущ ru m a 3°a'", 'сущ ru m a 3°a^', "сущ ru m a 3°a^'", 'сущ ru m a 3°b', 'сущ ru m a 4a', 'сущ ru m a 4b', 'сущ ru m a 4c', 'сущ ru m a 4c(1)', 'сущ ru m a 4c^', 'сущ ru m a 5*a', 'сущ ru m a 5*b', 'сущ ru m a 5a', 'сущ ru m a 5b', 'сущ ru m a 6*b', 'сущ ru m a 6a', 'сущ ru m a 6b', 'сущ ru m a 6c', 'сущ ru m a 7a', 'сущ ru m a 7a(3)', 'сущ ru m a 7b^', 'сущ ru m a-люди', 'сущ ru m a-человек', 'сущ ru m ina', 'сущ ru m ina  2a', 'сущ ru m ina (f 3a)', 'сущ ru m ina (n 3*a(1))', 'сущ ru m ina (n 4a((1)))', 'сущ ru m ina (n 4a(1))', 'сущ ru m ina (мс 1a)', 'сущ ru m ina (п 1a)', 'сущ ru m ina (п 1b)', 'сущ ru m ina (п 3a)', 'сущ ru m ina (с3*a(1))', 'сущ ru m ina (с3a(1))', 'сущ ru m ina (с4а(1))', 'сущ ru m ina 0', 'сущ ru m ina 1*a', 'сущ ru m ina 1*b', 'сущ ru m ina 1*c(1)', 'сущ ru m ina 1a', 'сущ ru m ina 1a((2))', 'сущ ru m ina 1a(2)', 'сущ ru m ina 1a^', 'сущ ru m ina 1b', 'сущ ru m ina 1b(1)', 'сущ ru m ina 1c', 'сущ ru m ina 1c(1)', 'сущ ru m ina 1c(1) // 1a', 'сущ ru m ina 1c(1)(2)', 'сущ ru m ina 1c(1)^', 'сущ ru m ina 1c(2)', 'сущ ru m ina 1d^', 'сущ ru m ina 1e', 'сущ ru m ina 1e // 1c(1)', 'сущ ru m ina 1e(2)', 'сущ ru m ina 1°a^-и', 'сущ ru m ina 2*a', 'сущ ru m ina 2*a^', 'сущ ru m ina 2*b', 'сущ ru m ina 2*e', 'сущ ru m ina 2a', 'сущ ru m ina 2a^', 'сущ ru m ina 2b', 'сущ ru m ina 2b(1)', 'сущ ru m ina 2c', 'сущ ru m ina 2c(1)', 'сущ ru m ina 2d^', 'сущ ru m ina 2e', 'сущ ru m ina 2f', 'сущ ru m ina 3*a', 'сущ ru m ina 3*a((2))', 'сущ ru m ina 3*a(2)', 'сущ ru m ina 3*b', 'сущ ru m ina 3*b(1)', 'сущ ru m ina 3*b(2)', 'сущ ru m ina 3*b^', 'сущ ru m ina 3*bx', 'сущ ru m ina 3*d', 'сущ ru m ina 3*d(2)', 'сущ ru m ina 3*d^', 'сущ ru m ina 3a', 'сущ ru m ina 3ax', 'сущ ru m ina 3b', 'сущ ru m ina 3b(1)', 'сущ ru m ina 3b(2)', 'сущ ru m ina 3c', 'сущ ru m ina 3c(1)', 'сущ ru m ina 3d^', 'сущ ru m ina 3e', 'сущ ru m ina 3°a', "сущ ru m ina 3°a'", 'сущ ru m ina 4a', 'сущ ru m ina 4b', 'сущ ru m ina 4c', 'сущ ru m ina 4e', 'сущ ru m ina 5*a', 'сущ ru m ina 5*b', 'сущ ru m ina 5a', 'сущ ru m ina 5a(2)', 'сущ ru m ina 5b', 'сущ ru m ina 6*a', 'сущ ru m ina 6*b', 'сущ ru m ina 6a', 'сущ ru m ina 6b', 'сущ ru m ina 6c', 'сущ ru m ina 6c(1)', 'сущ ru m ina 7a', 'сущ ru m ina 7a(3)', 'сущ ru m ina 7b', 'сущ ru m ina 7c(3)', 'сущ ru m ina 8b', 'сущ ru n a', 'сущ ru n a (1a)', 'сущ ru n a (ж2a)', 'сущ ru n a (п 1a)', 'сущ ru n a (п 3a)', 'сущ ru n a (п 4a)', 'сущ ru n a (п 4a-ся)', 'сущ ru n a 0', 'сущ ru n a 1*d', 'сущ ru n a 1*d^', 'сущ ru n a 1a', 'сущ ru n a 1b', 'сущ ru n a 1b(1)(2)', 'сущ ru n a 2b', 'сущ ru n a 3*a(1)', 'сущ ru n a 4a', 'сущ ru n a 5*a', 'сущ ru n a 5*a(2)', 'сущ ru n a 5*b', 'сущ ru n a 5a', 'сущ ru n a 5d', 'сущ ru n a 6*a(2)-m', 'сущ ru n a 6*b', 'сущ ru n a 7a', 'сущ ru n ina', 'сущ ru n ina  6*a', 'сущ ru n ina (1a)', 'сущ ru n ina (5?)', 'сущ ru n ina (п 1a)', 'сущ ru n ina (п 1a-)', 'сущ ru n ina (п 1b)', 'сущ ru n ina (п 1b-)', 'сущ ru n ina (п 3a)', 'сущ ru n ina (п 3b)', 'сущ ru n ina (п 4a)', 'сущ ru n ina (с6*a(2))', 'сущ ru n ina 0', 'сущ ru n ina 1*a', 'сущ ru n ina 1*b', 'сущ ru n ina 1*b^', 'сущ ru n ina 1*c^', 'сущ ru n ina 1*d', 'сущ ru n ina 1*d^', 'сущ ru n ina 1*d^-ь', 'сущ ru n ina 1a', 'сущ ru n ina 1a((1))', 'сущ ru n ina 1a^', 'сущ ru n ina 1a^-и', 'сущ ru n ina 1a^-р', 'сущ ru n ina 1b', 'сущ ru n ina 1b^', 'сущ ru n ina 1c', 'сущ ru n ina 1c^', 'сущ ru n ina 1c^-но', 'сущ ru n ina 1d', 'сущ ru n ina 1d^', 'сущ ru n ina 1f', 'сущ ru n ina 2a', 'сущ ru n ina 2c', 'сущ ru n ina 3*a(1)', 'сущ ru n ina 3*a(1)(2)', 'сущ ru n ina 3*b(1)(2)', 'сущ ru n ina 3*c(2)', 'сущ ru n ina 3*d(1)', 'сущ ru n ina 3a', 'сущ ru n ina 3a(1)', 'сущ ru n ina 3a(1)(2)', 'сущ ru n ina 3ax', 'сущ ru n ina 3b', 'сущ ru n ina 3c', 'сущ ru n ina 3c(2)', 'сущ ru n ina 3d(1)', 'сущ ru n ina 3e^', 'сущ ru n ina 4a', 'сущ ru n ina 4a^', 'сущ ru n ina 4f(1)', 'сущ ru n ina 5*a', 'сущ ru n ina 5*a((2))', 'сущ ru n ina 5*a(2)', 'сущ ru n ina 5*b', 'сущ ru n ina 5*b(2)', 'сущ ru n ina 5*c', 'сущ ru n ina 5*d', 'сущ ru n ina 5*d(2)', 'сущ ru n ina 5*d^', 'сущ ru n ina 5*f', 'сущ ru n ina 5a', 'сущ ru n ina 5b', 'сущ ru n ina 5d', 'сущ ru n ina 6*a', 'сущ ru n ina 6*a((2))', 'сущ ru n ina 6*a(2)', 'сущ ru n ina 6*b', 'сущ ru n ina 6*b?', 'сущ ru n ina 6*d', 'сущ ru n ina 6*d(2)', 'сущ ru n ina 6*d^', 'сущ ru n ina 7a', 'сущ ru n ina 7b', 'сущ ru n ina 7b(2)', 'сущ ru n ina 7b-^', 'сущ ru n ina 7b^', 'сущ ru n ina 8°a', 'сущ ru n ina 8°c', 'сущ ru n ina 8°c^', 'сущ ru пол1', 'сущ ru пол2', 'сущ ru+', 'сущ ru-old', 'сущ ru-old f a', 'сущ ru-old f a 1a', 'сущ ru-old f ina', 'сущ ru-old f ina 1a', 'сущ ru-old f ina 1d', 'сущ ru-old f ina 2a', 'сущ ru-old f ina 5a', 'сущ ru-old m a', 'сущ ru-old m a 1a', 'сущ ru-old m a 3b', 'сущ ru-old m a 5*a', 'сущ ru-old m a 5*b', 'сущ ru-old m ina', 'сущ ru-old m ina 1a', 'сущ ru-old m ina 1c', 'сущ ru-old m ina 1c(1)', 'сущ ru-old m ina 3b', 'сущ ru-old m ina 3c', 'сущ ru-old m ina 3c(1)', 'сущ ru-old n ina', 'сущ ru-old n ina 1a', 'сущ ru-old n ina 1c', 'сущ ru-old n ina 3*a(1)', 'сущ ru_пол1', 'сущ rue', 'сущ rue f', 'сущ rue f a', 'сущ rue f ina', 'сущ rue m', 'сущ rue m a', 'сущ rue m ina', 'сущ rue m una', 'сущ rue n', 'сущ rue n ina', 'сущ run', 'сущ rup', 'сущ rup f', 'сущ rut', 'сущ rut\u200e', 'сущ-ru', 'форма-сущ',
                        'фам 0', 'фам en s', 'фам ru', 'фам ru 0', 'фам ru f 1a', 'фам ru f 2*a', 'фам ru f 2a', 'фам ru f 2b', 'фам ru f 3a', 'фам ru f 4a', 'фам ru m 1a', 'фам ru m 1b', 'фам ru m 2a', 'фам ru m 3*a', 'фам ru m 3*b', 'фам ru m 3a', 'фам ru m 3b', 'фам ru m 4*b', 'фам ru m 4a', 'фам ru m 6a', 'фам ru {{{тип', 'фам ru ин', 'фам ru ин ов', 'фам ru ин-1b', 'фам ru иностр-м', 'фам ru ло', 'фам ru неизм', 'фам ru прил 1a', 'фам ru прил 1b', 'фам ru прил 3a', 'фам ru прил 3b', 'фам ru прил 4a', 'фам uk ко', 'фам uk ов', 'фам гриб', 'фам дзе', 'фам ин', 'фам ин ов', 'фам иностр-м', 'фам ко', 'фам козёл', 'фам неизм', 'фам рь', 'фам'],
    wt.ADJECTIVE     : ['прилагательное', '(прилагательное)', 'прил ru', 'прил ru  1*a', 'прил ru (мс 6*a)', 'прил ru 0', 'прил ru 1*a', "прил ru 1*a'", "прил ru 1*a'-", 'прил ru 1*a((1))', 'прил ru 1*a(1)', 'прил ru 1*a(1)-', 'прил ru 1*a(2)', 'прил ru 1*a-', 'прил ru 1*a/b', 'прил ru 1*a/b(2)', 'прил ru 1*a/b~', 'прил ru 1*a/c', 'прил ru 1*a/c"', "прил ru 1*a/c'", "прил ru 1*a/c'~", 'прил ru 1*ax', 'прил ru 1*a~', 'прил ru 1*b', 'прил ru 1*b/c"', "прил ru 1*b/c'", 'прил ru 1*b^', 'прил ru 1a', "прил ru 1a'", "прил ru 1a'~", 'прил ru 1a-', 'прил ru 1a/b', 'прил ru 1a/c', 'прил ru 1a/c"', "прил ru 1a/c'", "прил ru 1a/c'~", 'прил ru 1a/c-ё', 'прил ru 1a/c~', 'прил ru 1a?', 'прил ru 1a?10', 'прил ru 1a?7', 'прил ru 1a^', 'прил ru 1b', 'прил ru 1b/c', "прил ru 1b/c'", "прил ru 1b/c'~", 'прил ru 1b/c~', 'прил ru 1b/c~^', 'прил ru 1b?', 'прил ru 1bx', 'прил ru 2*a', 'прил ru 2*a-', 'прил ru 2*a^', 'прил ru 2a', 'прил ru 2a/c', 'прил ru 3*a', "прил ru 3*a'", 'прил ru 3*a/b', 'прил ru 3*a/c', 'прил ru 3*a/c"', "прил ru 3*a/c'", "прил ru 3*a/c'^-к", 'прил ru 3*a/c^', 'прил ru 3*ax~', 'прил ru 3*a~', 'прил ru 3a', "прил ru 3a'", "прил ru 3a'~", 'прил ru 3a/b~', 'прил ru 3a/c', 'прил ru 3a/c"', 'прил ru 3a/c"~', "прил ru 3a/c'", 'прил ru 3a^', 'прил ru 3a^+', 'прил ru 3ax~', 'прил ru 3a~', 'прил ru 3b', 'прил ru 3b/c', "прил ru 3b/c'", "прил ru 3b/c'~", 'прил ru 3b/c~', 'прил ru 3bx~', 'прил ru 4a', 'прил ru 4a-ся', 'прил ru 4a/b', "прил ru 4a/b'", 'прил ru 4a/b~', 'прил ru 4a/c', 'прил ru 4ax', 'прил ru 4ax~', 'прил ru 4b', 'прил ru 4bx', 'прил ru 4b~^', 'прил ru 5a', 'прил ru 6a', 'прил ru сравн', 'прил ru-old', 'прил ru-old 3ax~', 'прил rue', 'прил rup'],
    wt.VERB          : ['глагол', 'как самостоятельный глагол', 'в значении вспомогательного глагола или связки', '(глагол)', '(как самостоятельный глагол)', '(в значении вспомогательного глагола или связки)', 'гл ru', 'гл ru  1a-ся', 'гл ru  2a', 'гл ru  нсв', 'гл ru  св', 'гл ru -сянсв', 'гл ru -сясв', 'гл ru 10a-сясв', 'гл ru 10aсв', 'гл ru 10c', 'гл ru 10c-ся', 'гл ru 10c-сясв', 'гл ru 10c^-сясв', 'гл ru 10c^св', 'гл ru 10cсв', 'гл ru 11*b-сясв', 'гл ru 11*b/c"-сясв', 'гл ru 11*b/c"св', 'гл ru 11*b/c(1)св', 'гл ru 11*b/c^св', 'гл ru 11*b/cсв', 'гл ru 11*bсв', 'гл ru 11a-сясв', 'гл ru 11aсв', 'гл ru 11b', 'гл ru 11b((1))св', 'гл ru 11b-ся', 'гл ru 11b-сясв', 'гл ru 11b/c', 'гл ru 11b/c"-сясв', "гл ru 11b/c''-ся", 'гл ru 11b/c(1)св', 'гл ru 11b/c-ся', 'гл ru 11b/cсв', 'гл ru 11bсв', 'гл ru 12a', 'гл ru 12a-сясв', 'гл ru 12a-ы', 'гл ru 12a-ы-ся', 'гл ru 12aсв', 'гл ru 12b', 'гл ru 12b/c', 'гл ru 12b/cсв', 'гл ru 12b^-сясв', 'гл ru 12bсв', 'гл ru 13b', 'гл ru 13b-ся', 'гл ru 13bxсв', 'гл ru 14*b-мсв', 'гл ru 14*b-сясв', 'гл ru 14*bсв', 'гл ru 14aсв', 'гл ru 14b', 'гл ru 14b-ся', 'гл ru 14b-сясв', 'гл ru 14b/b-й-сясв', 'гл ru 14b/b-сясв', 'гл ru 14b/b^-сясв', 'гл ru 14b/c"-сясв', "гл ru 14b/c'св", 'гл ru 14b/c((1))св', 'гл ru 14b/c(1)-св', 'гл ru 14b/c(1)св', 'гл ru 14b/cсв', 'гл ru 14bсв', 'гл ru 14c(1)св', 'гл ru 14c/b-сясв', 'гл ru 14c/c"-сясв', 'гл ru 14c/c((1))св', 'гл ru 14c/c(1)св', 'гл ru 14c/cсв', 'гл ru 14cсв', 'гл ru 15a', 'гл ru 15a-сясв', 'гл ru 15axсв', 'гл ru 15aсв', 'гл ru 16aсв', 'гл ru 16b/c', 'гл ru 16b/c((1))св', 'гл ru 16b/c(1)св', 'гл ru 16b/c-ся', 'гл ru 16b/c-сясв', 'гл ru 16b/cсв', 'гл ru 1a', 'гл ru 1a нсв', "гл ru 1a'", 'гл ru 1a(7)', 'гл ru 1a(7)св', 'гл ru 1a-ся', 'гл ru 1a-сясв', 'гл ru 1a-ёсв', 'гл ru 1ax', 'гл ru 1ax^', 'гл ru 1ax^-ся', 'гл ru 1axсв', 'гл ru 1aсв', 'гл ru 2a', 'гл ru 2a-ся', 'гл ru 2a-сясв', 'гл ru 2ax', 'гл ru 2aсв', 'гл ru 2b', 'гл ru 2b-ся', 'гл ru 2b-сясв', 'гл ru 2bсв', 'гл ru 3a', 'гл ru 3a((3))-сясв', 'гл ru 3a((3))св', 'гл ru 3a(2)-сясв', 'гл ru 3a(2)св', 'гл ru 3a(3)-сясв', 'гл ru 3a(3)св', 'гл ru 3a-г', 'гл ru 3a-г-сясв', 'гл ru 3a-гсв', 'гл ru 3a-ся', 'гл ru 3a-сясв', 'гл ru 3aсв', 'гл ru 3b', 'гл ru 3b-ся', 'гл ru 3b-сясв', 'гл ru 3b-ёсв', 'гл ru 3bxсв', 'гл ru 3bсв', 'гл ru 3c', 'гл ru 3c-ся', 'гл ru 3c-сясв', 'гл ru 3cxсв', 'гл ru 3cсв', 'гл ru 3°a', 'гл ru 3°a((5)(6))', 'гл ru 3°a((5)(6))-г', 'гл ru 3°a((5)(6))-сясв', 'гл ru 3°a((5)(6))св', 'гл ru 3°a((5))(6)', 'гл ru 3°a((5))(6)-г', 'гл ru 3°a((6))-сясв', 'гл ru 3°a((6))св', 'гл ru 3°a(5)(6)', 'гл ru 3°a(5)(6)-сясв', 'гл ru 3°a(5)(6)св', 'гл ru 3°a(6)-гсв', 'гл ru 3°a(6)-сясв', 'гл ru 3°a(6)св', 'гл ru 3°a-гсв', 'гл ru 3°a-сясв', 'гл ru 3°aсв', 'гл ru 4a', 'гл ru 4a((2))', 'гл ru 4a((2))-л', 'гл ru 4a((2))-л-ся', 'гл ru 4a((2))-л-сясв', 'гл ru 4a((2))-т', 'гл ru 4a((2))-т-сясв', 'гл ru 4a((2))-тсв', 'гл ru 4a((2))-ш', 'гл ru 4a((2))-ш-ся', 'гл ru 4a((3))', 'гл ru 4a((3))((7))св', 'гл ru 4a((3))-б', 'гл ru 4a((3))-л', 'гл ru 4a((3))-л-ся', 'гл ru 4a((3))-л-сясв', 'гл ru 4a((3))-лсв', 'гл ru 4a((3))-ся', 'гл ru 4a((3))-сясв', 'гл ru 4a((3))-т', 'гл ru 4a((3))-т-сясв', 'гл ru 4a((3))-тсв', 'гл ru 4a((3))-ш', 'гл ru 4a((3))-ш-сясв', 'гл ru 4a((3))-шсв', 'гл ru 4a((3))св', 'гл ru 4a(2)-вы-жсв', 'гл ru 4a(2)св', 'гл ru 4a(3)', 'гл ru 4a(3)-чсв', 'гл ru 4a(3)-ш', 'гл ru 4a(3)-ш-сясв', 'гл ru 4a(3)св', 'гл ru 4a(7)-тсв', 'гл ru 4a-cc', 'гл ru 4a-б', 'гл ru 4a-б-ссв', 'гл ru 4a-б-ся', 'гл ru 4a-б-сясв', 'гл ru 4a-бсв', 'гл ru 4a-г-ся', 'гл ru 4a-г-сясв', 'гл ru 4a-гсв', 'гл ru 4a-ж-ь', 'гл ru 4a-и', 'гл ru 4a-и-ся', 'гл ru 4a-и-сясв', 'гл ru 4a-иx', 'гл ru 4a-иxсв', 'гл ru 4a-исв', 'гл ru 4a-й', 'гл ru 4a-й-ся', 'гл ru 4a-й-сясв', 'гл ru 4a-йсв', 'гл ru 4a-л-и', 'гл ru 4a-л-и-ся', 'гл ru 4a-л-и-сясв', 'гл ru 4a-л-исв', 'гл ru 4a-л-сясв', 'гл ru 4a-л-ь', 'гл ru 4a-л-ь-ся', 'гл ru 4a-л-ь-сясв', 'гл ru 4a-л-ьсв', 'гл ru 4a-лсв', 'гл ru 4a-р', 'гл ru 4a-с-л-сясв', 'гл ru 4a-с-ся', 'гл ru 4a-сс-сясв', 'гл ru 4a-сссв', 'гл ru 4a-стелитьсв', 'гл ru 4a-ся', 'гл ru 4a-сясв', 'гл ru 4a-т', 'гл ru 4a-т((2))', 'гл ru 4a-т((2))-ся', 'гл ru 4a-т-и', 'гл ru 4a-т-и-ся', 'гл ru 4a-т-и-сясв', 'гл ru 4a-т-исв', 'гл ru 4a-т-с-сясв', 'гл ru 4a-т-ся', 'гл ru 4a-т-сясв', 'гл ru 4a-т-ь', 'гл ru 4a-т-ь-ся', 'гл ru 4a-т-ь-сясв', 'гл ru 4a-т-ьсв', 'гл ru 4a-т2', 'гл ru 4a-т2-ся', 'гл ru 4a-тx', 'гл ru 4a-тxсв', 'гл ru 4a-тсв', 'гл ru 4a-ш', 'гл ru 4a-ш-и', 'гл ru 4a-ш-и-ся', 'гл ru 4a-ш-и-сясв', 'гл ru 4a-ш-исв', 'гл ru 4a-ш-с', 'гл ru 4a-ш-ся', 'гл ru 4a-ш-сясв', 'гл ru 4a-ш-ь', 'гл ru 4a-ш-ь-ся', 'гл ru 4a-ш-ь-сясв', 'гл ru 4a-ш-ьсв', 'гл ru 4a-шx', 'гл ru 4a-шс-сясв', 'гл ru 4a-шсв', 'гл ru 4a-шссв', 'гл ru 4a-ь', 'гл ru 4a-ь-безл-ся', 'гл ru 4a-ь-ся', 'гл ru 4a-ь-сясв', 'гл ru 4a-ьсв', 'гл ru 4ax', 'гл ru 4aсв', 'гл ru 4b', 'гл ru 4b((8))', 'гл ru 4b((8))-л', 'гл ru 4b((8))-лсв', 'гл ru 4b((8))-тсв', 'гл ru 4b((8))св', 'гл ru 4b(8)', 'гл ru 4b(8)-л', 'гл ru 4b(8)-лсв', 'гл ru 4b(8)-т', 'гл ru 4b(8)-тсв', 'гл ru 4b(8)-ш', 'гл ru 4b(8)-шсв', 'гл ru 4b(8)св', 'гл ru 4b-б', 'гл ru 4b-б-ся', 'гл ru 4b-б-сясв', 'гл ru 4b-бсв', 'гл ru 4b-клеймить', 'гл ru 4b-л', 'гл ru 4b-л-ся', 'гл ru 4b-л-сясв', 'гл ru 4b-лсв', 'гл ru 4b-ся', 'гл ru 4b-сясв', 'гл ru 4b-т', 'гл ru 4b-т-ся', 'гл ru 4b-т-сясв', 'гл ru 4b-тсв', 'гл ru 4b-ш', 'гл ru 4b-ш-безл', 'гл ru 4b-ш-ся', 'гл ru 4b-ш-сясв', 'гл ru 4b-шсв', 'гл ru 4b-щсв', 'гл ru 4b/c"-сясв', 'гл ru 4b/c-тсв', 'гл ru 4b^-тсв', 'гл ru 4bx', 'гл ru 4bx-тсв', 'гл ru 4bx^', 'гл ru 4bсв', 'гл ru 4c', 'гл ru 4c((4))', 'гл ru 4c((4))(7)', 'гл ru 4c((4))-б', 'гл ru 4c((4))-т', 'гл ru 4c(4)', 'гл ru 4c(4)(7)', 'гл ru 4c(4)-б', 'гл ru 4c(4)-л-ся', 'гл ru 4c(4)-ся', 'гл ru 4c(4)-т', 'гл ru 4c(4)-т-ся', 'гл ru 4c(4)-ш', 'гл ru 4c(4)-ш-ся', 'гл ru 4c(7)', 'гл ru 4c(7)-сясв', 'гл ru 4c(7)-т', 'гл ru 4c(7)-т-ждсв', 'гл ru 4c(7)-тсв', 'гл ru 4c(7)-ш', 'гл ru 4c(7)-шсв', 'гл ru 4c(7)св', 'гл ru 4c-б', 'гл ru 4c-бсв', 'гл ru 4c-л-ся', 'гл ru 4c-л-сясв', 'гл ru 4c-лсв', 'гл ru 4c-стелить', 'гл ru 4c-стелитьсв', 'гл ru 4c-стелиться', 'гл ru 4c-ся', 'гл ru 4c-сясв', 'гл ru 4c-т', 'гл ru 4c-т-ся', 'гл ru 4c-т-сясв', 'гл ru 4c-т?-сясв', 'гл ru 4c-тсв', 'гл ru 4c-ш', 'гл ru 4c-ш-ся', 'гл ru 4c-ш-сясв', 'гл ru 4c-шсв', 'гл ru 4cсв', 'гл ru 5*c/c"^-сясв', 'гл ru 5*c/cсв', 'гл ru 5a*xсв', 'гл ru 5a-л-сясв', 'гл ru 5a-ся', 'гл ru 5a-сясв', 'гл ru 5a-т', 'гл ru 5a-т-г', 'гл ru 5a-т-ся', 'гл ru 5a-т-сясв', 'гл ru 5a-тx', 'гл ru 5a-тсв', 'гл ru 5a-ш', 'гл ru 5a-ш-исв', 'гл ru 5a-шсв', 'гл ru 5a-я-сясв', 'гл ru 5a-ясв', 'гл ru 5a^-гн-св', 'гл ru 5a^-дсв', 'гл ru 5a^св', 'гл ru 5axсв', 'гл ru 5aсв', 'гл ru 5b', 'гл ru 5b-б', 'гл ru 5b-дсв', 'гл ru 5b-ж', 'гл ru 5b-ж-ся', 'гл ru 5b-ж-сясв', 'гл ru 5b-жсв', 'гл ru 5b-л', 'гл ru 5b-л-сясв', 'гл ru 5b-лx', 'гл ru 5b-лсв', 'гл ru 5b-м', 'гл ru 5b-мсв', 'гл ru 5b-ся', 'гл ru 5b-сясв', 'гл ru 5b-т', 'гл ru 5b-т-ся', 'гл ru 5b-т-сясв', 'гл ru 5b-тсв', 'гл ru 5b-ш', 'гл ru 5b-ш-ся', 'гл ru 5b-ш-сясв', 'гл ru 5b-шx', 'гл ru 5b-шсв', 'гл ru 5b-ёсв', 'гл ru 5b/c', 'гл ru 5b/c"-ся', 'гл ru 5b/c-л-сясв', 'гл ru 5b/c-лсв', 'гл ru 5b^', 'гл ru 5b^-т', 'гл ru 5b^-т2', 'гл ru 5b^св', 'гл ru 5bx-шсв', 'гл ru 5bxсв', 'гл ru 5bсв', 'гл ru 5c', "гл ru 5c'^-т", "гл ru 5c'^-т-ся", "гл ru 5c'^-т-сясв", "гл ru 5c'^-тсв", 'гл ru 5c(4)-ш', 'гл ru 5c(4)-ш-ся', 'гл ru 5c(4)x-л', 'гл ru 5c-е', 'гл ru 5c-е-ся', 'гл ru 5c-есв', 'гл ru 5c-ся', 'гл ru 5c-сясв', 'гл ru 5c-т', 'гл ru 5c-т-ся', 'гл ru 5c-т-сясв', 'гл ru 5c-тсв', 'гл ru 5c-ш-сясв', 'гл ru 5c-шсв', 'гл ru 5c/c', 'гл ru 5c/c"^-ся', 'гл ru 5c/c"^-сясв', 'гл ru 5c/c^св', 'гл ru 5cx-лсв', 'гл ru 5cсв', 'гл ru 6*c^св', 'гл ru 6a', 'гл ru 6a((3))-тсв', 'гл ru 6a(2)^-сясв', 'гл ru 6a-@св', 'гл ru 6a-б', 'гл ru 6a-б-сясв', 'гл ru 6a-бсв', 'гл ru 6a-г', 'гл ru 6a-г-ся', 'гл ru 6a-емлю', 'гл ru 6a-н', 'гл ru 6a-п-сясв', 'гл ru 6a-ся', 'гл ru 6a-сясв', 'гл ru 6a-т', 'гл ru 6a-т-г-сясв', 'гл ru 6a-т-и', 'гл ru 6a-т-исв', 'гл ru 6a-т-ся', 'гл ru 6a-т-сясв', 'гл ru 6a-тсв', 'гл ru 6a-ш', 'гл ru 6a^', 'гл ru 6a^-б', 'гл ru 6a^-б-ся', 'гл ru 6a^-бсв', 'гл ru 6a^-ся', 'гл ru 6a^-сясв', 'гл ru 6a^-т', 'гл ru 6a^св', 'гл ru 6axсв', 'гл ru 6aсв', 'гл ru 6b-ся', 'гл ru 6b-ш', 'гл ru 6b-шсв', 'гл ru 6b-я-сясв', 'гл ru 6b-я^', 'гл ru 6b-я^св', 'гл ru 6b^', 'гл ru 6b^-ся', 'гл ru 6b^св', 'гл ru 6bсв', 'гл ru 6c', 'гл ru 6c(7)св', 'гл ru 6c-бсв', 'гл ru 6c-л', 'гл ru 6c-л-ся', 'гл ru 6c-л-сясв', 'гл ru 6c-лсв', 'гл ru 6c-ся', 'гл ru 6c-сясв', 'гл ru 6c-т', 'гл ru 6c-т-сясв', 'гл ru 6c^св', 'гл ru 6cx', 'гл ru 6cx^', 'гл ru 6cx^св', 'гл ru 6cxсв', 'гл ru 6cсв', 'гл ru 6cсвyggg', 'гл ru 6°*b/c"-сясв', 'гл ru 6°*b/c^', 'гл ru 6°*b/c^св', 'гл ru 6°a', 'гл ru 6°a-ся', 'гл ru 6°a-сясв', 'гл ru 6°aсв', 'гл ru 6°b', 'гл ru 6°b-ся', 'гл ru 6°b-сясв', 'гл ru 6°b/c', 'гл ru 6°b/c"-сясв', 'гл ru 6°b/c-', 'гл ru 6°b/c-св', 'гл ru 6°b/c-ся', 'гл ru 6°b/c-сясв', 'гл ru 6°b/c^', 'гл ru 6°b/c^св', 'гл ru 6°b/cw', 'гл ru 6°b/cx', 'гл ru 6°b/cx-ся', 'гл ru 6°b/cx1^', 'гл ru 6°b/cx1^-ся', 'гл ru 6°b/cx1^-сясв', 'гл ru 6°b/cx1^св', 'гл ru 6°b/cx^-сясв', 'гл ru 6°b/cxсв', 'гл ru 6°b/cсв', 'гл ru 6°bсв', 'гл ru 6°c', 'гл ru 6°c^св', 'гл ru 7a', 'гл ru 7a((3))св', 'гл ru 7a(3)св', 'гл ru 7a(9)-дсв', 'гл ru 7a(9)-ссв', 'гл ru 7a-исв', 'гл ru 7a-с(9)св', 'гл ru 7a-сясв-д(9)', 'гл ru 7a^', 'гл ru 7a^-д-сясв', 'гл ru 7aсв', 'гл ru 7aсв-вы-д', 'гл ru 7aсв-д', 'гл ru 7aсв-д(9)', 'гл ru 7aсв-т(9)', 'гл ru 7aсв-т-ся(9)', 'гл ru 7b', 'гл ru 7b-дсв', 'гл ru 7b-зть', 'гл ru 7b-зть-ся', 'гл ru 7b-зтьсв', 'гл ru 7b-ся', 'гл ru 7b-сясв', 'гл ru 7b/b', 'гл ru 7b/b(9)-дсв', 'гл ru 7b/b(9)-с-сясв', 'гл ru 7b/b(9)-т-сясв', 'гл ru 7b/b(9)-тсв', 'гл ru 7b/b(9)св', 'гл ru 7b/b(9)св^', 'гл ru 7b/b-д', 'гл ru 7b/b-д-ся', 'гл ru 7b/b-д-сясв', 'гл ru 7b/b-дx', 'гл ru 7b/b-дсв', 'гл ru 7b/b-с', 'гл ru 7b/b-с-ся', 'гл ru 7b/b-ст', 'гл ru 7b/b-ст-ся', 'гл ru 7b/b-стсв', 'гл ru 7b/b-ся', 'гл ru 7b/b-сянсв', 'гл ru 7b/b-сясв', 'гл ru 7b/b-т', 'гл ru 7b/b-т(9)св', 'гл ru 7b/b-т-ся', 'гл ru 7b/b-т-сяx', 'гл ru 7b/b-тx', 'гл ru 7b/b-тсв', 'гл ru 7b/b-ть', 'гл ru 7b/b^-ся', 'гл ru 7b/b^-сясв', 'гл ru 7b/b^-т(9)св', 'гл ru 7b/b^-т-сясв', 'гл ru 7b/bсв', 'гл ru 7bx', 'гл ru 7bx^', 'гл ru 7bx^-ся', 'гл ru 7bсв', 'гл ru 8*b/b-сясв', 'гл ru 8*b/bсв', 'гл ru 8a-гсв', 'гл ru 8a-ксв', 'гл ru 8a/b-сясв', 'гл ru 8a/bсв', 'гл ru 8aсв', 'гл ru 8b-гсв', 'гл ru 8b/b', 'гл ru 8b/b-ксв', 'гл ru 8b/b-ся', 'гл ru 8b/b-сясв', 'гл ru 8b/b^', 'гл ru 8b/bсв', 'гл ru 8b/c', 'гл ru 8b/cсв', 'гл ru 8c/b', 'гл ru 8c/b-ся', 'гл ru 8c/bсв', 'гл ru 9*a-сясв', 'гл ru 9*aсв', 'гл ru 9*b-сясв', 'гл ru 9*b/c(1)^св', 'гл ru 9*b/c(1)св', 'гл ru 9*bсв', 'гл ru 9b', 'гл ru 9b-ся', 'гл ru 9b-сясв', 'гл ru 9b/b-сясв', 'гл ru 9b/c"(1)-сясв', 'гл ru 9b/c"-сясв', 'гл ru 9b/c(1)св', 'гл ru 9bсв', 'гл ru ^a(9)св', 'гл ru ^a-быть-сясв', 'гл ru ^a-бытьсв', 'гл ru ^a-ех', 'гл ru ^a-ех-сясв', 'гл ru ^a-ехсв', 'гл ru ^a-зижд', 'гл ru ^a-зижд-ся', 'гл ru ^a-зиждсв', 'гл ru ^a-зыб', 'гл ru ^a-зыб-ся', 'гл ru ^a/c((1))св', 'гл ru ^a/c(1)св', 'гл ru ^a/cсв', 'гл ru ^a/с', 'гл ru ^aсв', 'гл ru ^b', 'гл ru ^b-б-сясв', 'гл ru ^b-бсв', 'гл ru ^b-в', 'гл ru ^b-в-сясв', 'гл ru ^b-всв', 'гл ru ^b-ся', 'гл ru ^b-сясв', 'гл ru ^b/b(9)', 'гл ru ^b/b(9)-', 'гл ru ^b/b(9)-сясв', 'гл ru ^b/b(9)св', 'гл ru ^b/c', 'гл ru ^b/c"-ся', 'гл ru ^b/c"-сясв', "гл ru ^b/c'св", 'гл ru ^b/c((1))-сясв', 'гл ru ^b/c((1))св', 'гл ru ^b/c((1))св-ся', 'гл ru ^b/c(1)св', 'гл ru ^b/c-клясть-сясв', 'гл ru ^b/c-клястьсв', 'гл ru ^b/c-сясв', 'гл ru ^b/cсв', 'гл ru ^bсв', 'гл ru нв', 'гл ru нсв', 'гл ru св', 'гл ru-old', 'гл ru-old 1a', 'гл ru-old 2a', 'гл rue', 'гл rup', 'гл rut'],
    wt.ADVERB        : ['adv ru', 'adv'],
    wt.PREDICATIVE   : ['predic ru', 'predic'],
    wt.CONJUNCTION   : ['conj ru', 'conj'],
    wt.PREPOSITION   : ['предлог', '(предлог)', 'prep ru'],
    wt.PRONOUN       : ['местоимение', '(местоимение)', 'мест ru', 'мест ru (п 2a)', 'мест ru 0', 'мест ru 1a-в', 'мест ru 1a-в\u200e', 'мест ru 1a-н', 'мест ru 1b', 'мест ru 2*a', 'мест ru 4a', 'мест ru 6*a-', 'мест ru 6*b', 'мест ru xx', 'мест ru вы', 'мест ru кто', 'мест ru некто', 'мест ru п 1a', 'мест ru п1*b', 'мест ru п1a', 'мест ru п1b', 'мест ru п1f', 'мест ru п2*b', 'мест ru п3a', 'мест ru п6*a', 'мест ru п6*b', 'мест ru п6a', 'мест ru п6b', 'мест ru сё', 'мест ru что', 'мест rue', 'мест rup'],
    wt.INTERJECTION  : ['междометие', '(междометие)', 'interj ru', 'interj', 'interj-ru'],
    wt.PARTICLE      : ['прич ru', 'прич ru  -ённ', 'прич ru -вш', 'прич ru -вш-ся', 'прич ru -ем', 'прич ru -енн', 'прич ru -им', 'прич ru -нн', 'прич ru -ущ', 'прич ru -ущ-ся', 'прич ru -ш', 'прич ru -ющ', 'прич ru -ющ-ся', 'прич ru -ящ', 'прич ru -ённ', "прич ru 1*a'(2)", 'прич ru 1*a(2)-енн', 'прич ru 1*a(2)-нн', 'прич ru 1*a/b(2)-нн', 'прич ru 1*a/b(2)-ённ', 'прич ru 1a', "прич ru 1a'", 'прич ru 1a-ем', 'прич ru 1a-им', "прич ru 1a-им'", 'прич ru 1a-ом', "прич ru 1a-ом'", 'прич ru 1a-т', 'прич ru 1a/c~-т', 'прич ru 4a', 'прич ru 4a-ащ', "прич ru 4a-ащ'", "прич ru 4a-ащ'-ся", 'прич ru 4a-ащ-ся', 'прич ru 4a-вш', 'прич ru 4a-вш-ся', 'прич ru 4a-ущ', "прич ru 4a-ущ'", "прич ru 4a-ущ'-ся", 'прич ru 4a-ш', 'прич ru 4a-ш-ся', 'прич ru 4a-ющ', "прич ru 4a-ющ'", "прич ru 4a-ющ'-ся", 'прич ru 4a-ющ-ся', 'прич ru 4a-ящ', "прич ru 4a-ящ'", "прич ru 4a-ящ'-ся", 'прич ru 4a-ящ-ся', 'part ru'],
    wt.ARTICLE       : ['статья'],
    wt.NUMERAL       : ['цифра', '(цифра)',
                        'родств:числ', 'форма-числ', 'форма-числ la', 'числ', 'числ ab', 'числ abq', 'числ ady', 'числ ae', 'числ af', 'числ ain', 'числ akm', 'числ akz', 'числ ale', 'числ alt', 'числ am', 'числ an', 'числ ang', 'числ aqc', 'числ ar', 'числ arc', 'числ arn', 'числ art', 'числ asm', 'числ ast', 'числ ast c', 'числ av', 'числ ay', 'числ az', 'числ ba', 'числ ba-ау', 'числ ba-әү', 'числ bar', 'числ be', 'числ be 3', 'числ ber', 'числ bg', 'числ bm', 'числ bn', 'числ bo', 'числ br', 'числ bs', 'числ bua', 'числ ca', 'числ ce', 'числ ceb', 'числ ch', 'числ chm', 'числ chm\u200e', 'числ chr', 'числ chy', 'числ cjs', 'числ ckb', 'числ ckt', 'числ cmn', 'числ co', 'числ co c', 'числ cop', 'числ crh', 'числ cs', 'числ csb', 'числ cu', 'числ cv', 'числ cy', 'числ cy f', 'числ da', 'числ dar', 'числ ddo', 'числ de', 'числ dlg', 'числ dng', 'числ dsb', 'числ el', 'числ eml', 'числ en', 'числ en c', 'числ en o', 'числ eo', 'числ es', 'числ es c', 'числ es o', 'числ et', 'числ eu', 'числ eve', 'числ evn', 'числ ewe', 'числ ext', 'числ fa', 'числ fi', 'числ fj', 'числ fo', 'числ fo ein', 'числ fo tríggir', 'числ fr', 'числ fr c', 'числ fr o', 'числ fro', 'числ fur', 'числ fy', 'числ ga', 'числ gag', 'числ gd', 'числ gdo', 'числ gin', 'числ gl', 'числ gld', 'числ gn', 'числ got', 'числ grc', 'числ gsw', 'числ gu', 'числ gv', 'числ ha', 'числ hak', 'числ haw', 'числ he', 'числ hi', 'числ hr', 'числ hsb', 'числ ht', 'числ hu', 'числ hy', 'числ ia', 'числ ia c', 'числ ibo', 'числ id', 'числ ik', 'числ ilo', 'числ inh', 'числ io', 'числ is', 'числ is n', 'числ it', 'числ it c', 'числ it o', 'числ itl', 'числ iu', 'числ ja', 'числ jbo', 'числ jct', 'числ jmy', 'числ jv', 'числ ka', 'числ kaa', 'числ kaa\u200e', 'числ kas', 'числ kbd', 'числ kca', 'числ kdr', 'числ kea', 'числ kem', 'числ ket', 'числ kg', 'числ kim', 'числ kjh', 'числ kjj', 'числ kk', 'числ kk c', 'числ kl', 'числ ko', 'числ koi', 'числ kok', 'числ kom', 'числ kpy', 'числ krc', 'числ krl', 'числ ku', 'числ kum', 'числ kw', 'числ ky', 'числ la', 'числ la ambo', 'числ la card 0', 'числ la card 1a', 'числ la duo', 'числ la ord 1a', 'числ la tres', 'числ la unus', 'числ lad', 'числ lb', 'числ lbe', 'числ lez', 'числ li', 'числ liv', 'числ lkt', 'числ lmo', 'числ ln', 'числ lo', 'числ lt', 'числ lt f', 'числ ltg', 'числ lug', 'числ lv', 'числ lzz', 'числ mas', 'числ mdf', 'числ mg', 'числ mi', 'числ mk', 'числ mn', 'числ mnc', 'числ mns', 'числ mo', 'числ moh', 'числ mr', 'числ mrj', 'числ ms', 'числ mt', 'числ mwl', 'числ my', 'числ myv', 'числ na', 'числ nah', 'числ nap', 'числ nds', 'числ ne', 'числ nio', 'числ nl', 'числ nn', 'числ no', 'числ nog', 'числ nov', 'числ nv', 'числ obt', 'числ oc', 'числ oj', 'числ om', 'числ or', 'числ orv', 'числ os', 'числ ota', 'числ otk', 'числ pa', 'числ pag', 'числ pal', 'числ pap', 'числ pau', 'числ pi', 'числ pl', 'числ pl кол', 'числ pl пор', 'числ pms', 'числ pox', 'числ prg', 'числ ps', 'числ pt', 'числ pt c', 'числ pt o', 'числ pt-br', 'числ qu', 'числ rap', 'числ rm', 'числ ro', 'числ ro c', 'числ ro o', 'числ roa-nor', 'числ rom', 'числ ru', 'числ ru -надесять', 'числ ru 20', 'числ ru 3', 'числ ru 4', 'числ ru 40-90', 'числ ru 7-8-десят', 'числ ru 8', 'числ ru дцать', 'числ ru оба', 'числ ru п 1a', 'числ ru п 1b', 'числ ru полтора', 'числ ru полтораста', 'числ ru ста', 'числ ru-old', 'числ rue', 'числ rup', 'числ rut', 'числ rw', 'числ sa', 'числ sah', 'числ sc', 'числ sc c', 'числ scn', 'числ scn c', 'числ sco', 'числ sd', 'числ se', 'числ sel', 'числ sgs', 'числ si', 'числ sjd', 'числ sk', 'числ sl', 'числ slovio', 'числ sm', 'числ smn', 'числ sms', 'числ sn', 'числ so', 'числ sq', 'числ sr', 'числ sr 1', 'числ srn', 'числ ss', 'числ st', 'числ sty', 'числ su', 'числ sv', 'числ sva', 'числ sw', 'числ szl', 'числ tab', 'числ tet', 'числ tg', 'числ th', 'числ tin', 'числ tir', 'числ tk', 'числ tkd', 'числ tl', 'числ tlh', 'числ tly', 'числ tn', 'числ to', 'числ tpi', 'числ tr', 'числ trp', 'числ tso', 'числ tt', 'числ ttt', 'числ ty', 'числ tyv', 'числ uby', 'числ udm', 'числ udm кол', 'числ udm пор', 'числ ug', 'числ uk', 'числ uk 3', 'числ ur', 'числ uum', 'числ uz', 'числ vai', 'числ vec', 'числ ven', 'числ vep', 'числ vi', 'числ vls', 'числ vo', 'числ vot', 'числ vro', 'числ wa', 'числ war', 'числ wo', 'числ wym', 'числ xal', 'числ xbm', 'числ xbo', 'числ xh', 'числ xmf', 'числ xog', 'числ xx', 'числ yi', 'числ yo', 'числ yrk', 'числ yua', 'числ za', 'числ ze', 'числ zu', 'числ zza', 'числ-2', 'числ-2 be', 'числ-20 be', 'числ-5', 'числ-5 be', 'числ-5-десят', 'числ-5-сот', 'числ-7-десят', 'числ-8-сот', 'числ-дцать', 'числ-ое', 'числ-собир1b', 'числ-собир3a', 'числ-ста', 'числ-тыс', 'числ.', 'числа ab', 'числа ady', 'числа art', 'числа ce', 'числа de', 'числа en', 'числа fr', 'числа la', 'числа nl', 'числа sq', 'числа vep', 'число букв', 'этимология:число'],
    wt.ABBREV        : ['abbrev'],
    wt.INTRO         : ['intro ru', 'intro-ru'],
}

TOS_SECTIONS = list( filter(None, ( (yield from v) for v in TYPE_OF_SPEECH.values() )) )

SECTION_NAME_TEMPLATES = { # === {{sustantivo femenino y masculino|es}} === -> sustantivo femenino y masculino
    s:lambda t: t.name for s in TOS_SECTIONS
}

SECTION_NAME_TEMPLATES.update({ # {{-nome-}} -> nome
    's'       : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)) if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    'з'       : lambda t: (t.arg(0).lower() if isinstance(t.arg(0), str) else t.arg(0)) if t.arg(1) is None or t.arg(1).lower().strip() in LANGUAGES else None,
    '-ru-'    : lambda t: "-ru-",
    '-cyrl-'  : lambda t: "-cyrl-",
    'заголовок': lambda t: t.arg(0),
})


def is_lang_template(t):
    pass

#
def is_lang_section(sec):
    if sec.name in LANG_SECTIONS:
        return True


def is_tos_section(sec):
    if sec.name in TOS_SECTIONS:
        return True
    elif has_template(sec.header, [], TYPE_OF_SPEECH):
        pass


def is_expl_section(sec):
    return sec.name == 'значение'


def verb_ru_1a(t):
    root = t.arg('основа')
    if not root:
        root = t.arg(0)
        
        if root:
            yield root + 'ю'
            yield root + 'л'
            yield root + 'ла'
            
            yield root + 'ешь'
            yield root + 'й'
            
            yield root + 'ет'
            yield root + 'ло'
            
            yield root + 'ем'
            yield root + 'ете'
            yield root + 'ли'
            yield root + 'йте'
            
            yield root + 'ют'
            
            yield root + 'ющий'
            yield root + 'вщий'
            
            yield root + 'я'
            yield root + 'в'
            yield root + 'вши'
            
            yield root + 'емый'
            
            yield root + 'ть'

    
def Type(search_context, excludes, word):
    sec = search_context
    
    for (tos, section_names) in TYPE_OF_SPEECH.items():
        if sec.name in section_names:
            word.Type = tos
            break


def IsMale(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['gramática', 'g'], 
            [has_arg, 0, [has_value, ['m', 'mp']]],
            [has_arg, 0, [has_value, ['m', 'mp']]]
        ],
        [has_template, 'm'], 
    ):
        word.IsMale = True


def IsFeminine(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['gramática', 'g'], 
            [has_arg, 0, [has_value, ['f', 'fp']]],
            [has_arg, 1, [has_value, ['f', 'fp']]]
        ],
        [has_template, 'f'], 
    ):
        word.IsMale = True


def IsNeutre(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['gramática', 'g'], 
            [has_arg, 0, [has_value, ['n', 'np', 'ns', 'n2n']]]
        ],
        [has_template, 'n'], 
    ):
        word.IsNeutre = True


def IsSingle(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['форма-сущ'], [has_arg, 2, [has_value, ['ед']]]],
    ):
        word.IsSingle = True


def IsPlural(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, ['форма-сущ'], [has_arg, 2, [has_value, ['мн']]]],
    ):
        word.IsPlural = True
    
    
def SingleVariant(search_context, excludes, word):
    # {{Форма-сущ|семя|именительного|мн}}
    for t in search_context.find_objects(Template, recursive=True, exclude=excludes):
        if t.name == 'форма-сущ':
            lang = t.arg(6)
            term = t.arg(0)
            sp = t.arg(2)
            if sp == 'мн':
                if lang is None or lang in LANGUAGES:
                    word.SingleVariant = term
                    break
        

def PluralVariant(search_context, excludes, word):
    # {{Форма-сущ|семя|именительного|ед}}
    for t in search_context.find_objects(Template, recursive=True, exclude=excludes):
        if t.name == 'форма-сущ':
            lang = t.arg(6)
            term = t.arg(0)
            sp = t.arg(2)
            if sp == 'ед':
                if lang is None or lang in LANGUAGES:
                    word.SingleVariant = term
                    break


def MaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['avi-for-fle'],
            [in_arg, (None, 0) ],
        ],
        [in_template, ['flex.pt.subst.completa', 'flex.pt'],
            [in_arg, (None, ['ms', 'msa', 'msd']) ],
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.MaleVariant = term
            break


def FemaleVariant(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['flex.pt.subst.completa', 'flex.pt'],
            [in_arg, (None, ['fs', 'fsa', 'fsd']) ],
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.FemaleVariant = term
            break
    

def IsVerbPast(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, 'прич.', [has_arg, 1, [has_value, 'прош']]],
    ):
        word.IsVerbPast = True
    

def IsVerbPresent(search_context, excludes, word):
    if if_any(search_context, excludes, 
        [has_template, 'прич.', [has_arg, 1, [has_value, 'наст']]],
    ):
        word.IsVerbPresent = True
    

def IsVerbFutur(search_context, excludes, word):
    pass
    

def Conjugation(search_context, excludes, word):
    for t in search_context.find_objects(Template, recursive=True, exclude=excludes):
        if t.name in ['гл ru 1a']:
            for term in verb_ru_1a(t):
                if term:
                    word.add_conjugation( 'ru', term )
    
    
def Synonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['синонимы'],
            [in_template, ['link', 'l', 'lb'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_synonym( lang, term )
    

def Antonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['антонимы'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_antonym( lang, term )


def Hypernymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['гиперонимы'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hypernym( lang, term )


def Hyponymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['гипонимы'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_hyponym( lang, term )


def Meronymy(search_context, excludes, word):
    pass


def Holonymy(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['holonímias'], 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_holonym( lang, term )

    
def Troponymy(search_context, excludes, word):
    pass


def Otherwise(search_context, excludes, word):
    pass


def AlternativeFormsOther(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_template, ['падежи'],
            [in_arg, (None, ['Кто/что? (ед) ', 'Кто/что? (мн) ', 'Нет кого/чего? (ед)', 'Нет кого/чего? (мн)', 
                'Кому/чему? (ед) ', 'Кому/чему? (мн) ', 'Кого/что? (ед) ', 'Кого/что? (мн) ', 'Кем/чем? (ед) ', 
                'Кем/чем? (мн) ', 'О ком/чём? (ед) ', 'О ком/чём? (мн) ']) ],
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_alternative_form( lang, term )    


def RelatedTerms(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, ['родственные слова', 'см. также'], 
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_related(lang, term)

    for t in search_context.find_objects(Template, recursive=True, exclude=excludes):
        if t.name in ['родств-блок']:
            for a in t.args():
                lang = None
                term = a.get_value()
                if term:
                    terms = [ term for term in term.replace(';', ',').split(',') ]
                    for term in terms:
                        if term:
                            word.add_related(lang, term.strip())
    
    for (lang, term) in find_all(search_context, excludes,
        [in_template, 'прич.', [in_arg, (None, 0)]],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_related(lang, term)



def Coordinate(search_context, excludes, word):
    for (lang, term) in find_all(search_context, excludes,
        [in_section, 'termos coordenados (koipônimos)', 
            [in_template, ['link', 'l'], [in_arg, (0, 1) ]],
            [in_link]
        ],
    ):
        if lang is None or lang in LANGUAGES:
            word.add_coordinate( lang, term )


def Translation(search_context, excludes, word):
    # {{trad|en|cat}} {{t+|fr|ongle|m}}
    for (lang, term) in find_all(search_context, excludes,
        [in_template, "trad"    , [in_arg, (["lang", 0], 1)]],
        [in_template, "trad-"   , [in_arg, (["lang", 0], 1)]],
        [in_template, "trad+"   , [in_arg, (["lang", 0], 1)]],
        [in_template, "t"       , [in_arg, (["lang", 0], 1)]],
        [in_template, "t-simple", [in_arg, (["lang", 0], 1)]],
        [in_template, "t+"      , [in_t_plus]],
    ):
        word.add_translation(lang, term)

    # Translations
    for section in search_context.find_objects(Section, recursive=False, exclude=excludes):
        if section.name in ['-trad-', '-trad1-', '-trad2-']:
            for li in section.find_objects(Li, recursive=False):
                for t in li.find_objects(Template, recursive=False):
                    lang = t.name
                    for link in li.find_objects(Link, recursive=False):
                        term = link.get_text()
                        word.add_translation(lang, term)
                    break

    for t in search_context.find_objects(Template, recursive=True, exclude=excludes):
        if t.name in ['перев-блок']:
            for a in t.args():
                lang = a.get_name()
                term = a.get_value()
                if lang and term:
                    word.add_translation(lang, term)


def LabelType(search_context, excludes, word):
    word.LabelType = get_label_type(search_context)


def ExplainationRaw(search_context, excludes, word):
    li = search_context
    word.ExplainationRaw = li.get_raw()
    
    
def ExplainationTxt(search_context, excludes, word):
    li = search_context
    word.ExplainationTxt = li.get_text().strip()
    
    
def ExplainationExamplesRaw(search_context, excludes, word):
    li = search_context
    for e in li.find_objects(Li, recursive=True):
        if e.base.endswith(":"):
            word.ExplainationExamplesRaw = e.get_raw()
            break
    
def ExplainationExamplesTxt(search_context, excludes, word):
    li = search_context
    for e in li.find_objects(Li, recursive=True):
        if e.base.endswith(":"):
            word.ExplainationExamplesTxt = e.get_text().strip()
            break

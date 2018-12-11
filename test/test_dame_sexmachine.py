#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2018  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GNU Emacs; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

import unittest
import numpy as np
from app.dame_sexmachine import Sexmachine

class TddInPythonExample(unittest.TestCase):

    def test_string2array_method_returns_correct_result(self):
        array = "muchos    espacios en blanco"
        s = Sexmachine()
        arr = s.string2array(array)
        self.assertEqual(["muchos", "espacios", "en", "blanco"], arr)


    def test_sexmachine_features_method_returns_correct_result(self):
        s = Sexmachine()
        f = s.features("David")
        self.assertEqual(f['has(a)'], True)
        self.assertEqual(f['count(i)'], 1)
        self.assertEqual(f['count(v)'], 1)
        self.assertEqual(f['last_letter'], 'd')
        self.assertEqual(f['first_letter'], 'd')

    def test_sexmachine_features_int_method_returns_correct_result(self):
        s = Sexmachine()
        f = s.features_int("David")
        self.assertTrue(f['syllables'] == 2)
        self.assertTrue(len(f) > 0)

    def test_sexmachine_guess_method_returns_correct_result(self):
        s = Sexmachine()
        self.assertEqual(s.guess("David"), 'male')
        self.assertEqual(s.guess("Laura"), 'female')
        self.assertEqual(s.guess("Inés"), 'female') # Con acento
        self.assertEqual(s.guess("Ines"), 'female') # Sin acento
        self.assertEqual(s.guess("Nodiccionario"), 'male') # Sin estar en diccionario
        self.assertEqual(s.guess("Nadiccionaria"), 'female') # En diccionario
        self.assertEqual(s.guess("David", binary=True), 1)
        self.assertEqual(s.guess("Laura", binary=True), 0)
        self.assertEqual(s.guess("Nodiccionario", binary=True), 1)
        self.assertEqual(s.guess("Nadiccionaria", binary=True), 0)

    def test_sexmachine_guess_surname_method_returns_correct_result(self):
        s = Sexmachine()
        self.assertTrue(s.guess_surname("Smith"))

    def test_sexmachine_guess_list_method_returns_correct_result(self):
        s = Sexmachine()
        self.assertEqual(['male', 'male', 'female', 'male', 'male', 'male', 'female', 'female', 'male', 'female', 'male', 'male', 'male', 'male', 'male', 'female', 'male', 'male', 'male', 'male', 'male'], s.guess_list(all=False, binary=False))
        self.assertEqual([1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1], s.guess_list(all=False,binary=True))
#        self.assertEqual([('"pierre"', 'male'), ('"raul"', 'male'), ('"adriano"', 'female'), ('"ralf"', 'male'), ('"teppei"', 'male'), ('"guillermo"', 'male'), ('"catherine"', 'female'), ('"sabina"', 'female'), ('"ralf"', 'male'), ('"karl"', 'female'), ('"sushil"', 'male'), ('"clemens"', 'male'), ('"gregory"', 'male'), ('"lester"', 'male'), ('"claude"', 'male'), ('"martin"', 'female'), ('"vlad"', 'male'), ('"pasquale"', 'male'), ('"lourdes"', 'male'), ('"bruno"', 'male'), ('"thomas"', 'male')], s.guess_list())

    def test_sexmachine_features_int_method_returns_correct_result(self):
        s = Sexmachine()
        dicc = s.features_int("David")
        self.assertEqual(chr(dicc['last_letter']), 'd')
        self.assertEqual(chr(dicc['first_letter']), 'd')
        self.assertEqual(dicc['count(a)'], 1)
        self.assertEqual(dicc['count(b)'], 0)
        self.assertEqual(dicc['count(c)'], 0)
        self.assertEqual(dicc['count(d)'], 2)
        self.assertEqual(dicc['count(e)'], 0)
        self.assertEqual(dicc['count(f)'], 0)
        self.assertEqual(dicc['count(h)'], 0)
        self.assertEqual(dicc['count(i)'], 1)
        self.assertEqual(dicc['count(v)'], 1)
        self.assertTrue(dicc['count(a)'] > 0)
        self.assertTrue(dicc['vocals'], 2)
        self.assertTrue(dicc['consonants'], 3)
        self.assertEqual(dicc['first_letter_vocal'], 0)
        self.assertEqual(dicc['last_letter_vocal'], 0)
        self.assertTrue(len(dicc.values()) > 30)

    def test_sexmachine_features_list_method_returns_correct_result(self):
        s = Sexmachine()
        fl = s.features_list()
        self.assertTrue(len(fl) > 20)

    def test_sexmachine_features_list_all_method_returns_correct_result(self):
        s = Sexmachine()
        fl = s.features_list(all=True)
        self.assertTrue(len(fl) > 1000)

    def test_sexmachine_gender_list_method_returns_correct_result(self):
        s = Sexmachine()
        gl = s.gender_list()
        self.assertEqual(gl, [1, 1, 1, 1, 2, 1, 0, 0, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1])
        self.assertEqual(len(gl), 21)
        self.assertEqual(s.females, 3)
        self.assertEqual(s.males, 16)
        self.assertEqual(s.unknown, 2)

    def test_sexmachine_gender_list_all_method_returns_correct_result(self):
        s = Sexmachine()
        gl = s.gender_list(all=True)
        self.assertTrue(len(gl) > 1000)

    def test_sexmachine_accuracy_method_returns_correct_result(self):
        s = Sexmachine()
        self.assertTrue(s.accuracy() > 0.5)

    def test_sexmachine_confusion_matrix_method_returns_correct_result(self):
        s = Sexmachine()
        cm = s.confusion_matrix()
        am = np.array([[2, 1, 0],[3, 13, 0],[0, 2, 0]])
        self.assertTrue(np.array_equal(cm,am))

    def test_sexmachine_string2gender_method_returns_correct_result(self):
        s = Sexmachine()
        gender1 = s.string2gender("Arroyo Menéndez, David")
        gender2 = s.string2gender("xxxxx Laura")
        self.assertTrue(gender1, 'male')
        self.assertTrue(gender2, 'female')


    # def test_sexmachine_svc_list_method_returns_correct_result(self):
    #     s = Sexmachine()
    #     m = s.svc()
    #     predicted = m.predict([[ 0,  0,  1,  0, 21,  0,  0,  0,  0, 34,  2,  0,  0,  0,  0,  0, 0,  0,  0,  5,  0,  0,  0,  0,  0,  2,  0,  0,  0, 34,  1,  0]])
    #     n = np.array([0])
    #     self.assertTrue(np.array_equal(predicted, n))

    # def test_sexmachine_sgd_list_method_returns_correct_result(self):
    #     s = Sexmachine()
    #     m = s.sgd()
    #     predicted = m.predict([[ 0,  0,  1,  0, 21,  0,  0,  0,  0, 34,  2,  0,  0,  0,  0,  0, 0,  0,  0,  5,  0,  0,  0,  0,  0,  2,  0,  0,  0, 34,  1,  0]])
    #     n = np.array([1])
    #     self.assertTrue(np.array_equal(predicted, n))

    # def test_sexmachine_gaussianNB_list_method_returns_correct_result(self):
    #     s = Sexmachine()
    #     m = s.gaussianNB()
    #     array = [[ 0,  0,  1,  0, 21,  0,  0,  0,  0, 34,  2,  0,  0,  0,  0,  0,
    #                0,  0,  0,  5,  0,  0,  0,  0,  0,  2,  0,  0,  0, 34,  1,  0],
    #              [ 0,  0,  0,  0, 21,  0,  0,  0,  0, 34,  0,  0,  0,  0,  0,  1,
    #                0,  0,  0,  5,  0,  0,  1,  0,  0,  1,  0,  0,  1, 34,  0,  0]]
    #     predicted= m.predict(array)
    #     n = np.array([2, 2])
    #     self.assertTrue(np.array_equal(predicted, n))


    # def test_sexmachine_multinomialNB_list_method_returns_correct_result(self):
    #     s = Sexmachine()
    #     m = s.multinomialNB()
    #     array = [[ 0,  0,  1,  0, 21,  0,  0,  0,  0, 34,  2,  0,  0,  0,  0,  0,
    #                0,  0,  0,  5,  0,  0,  0,  0,  0,  2,  0,  0,  0, 34,  1,  0],
    #              [ 0,  0,  0,  0, 21,  0,  0,  0,  0, 34,  0,  0,  0,  0,  0,  1,
    #                0,  0,  0,  5,  0,  0,  1,  0,  0,  1,  0,  0,  1, 34,  0,  0]]
    #     predicted= m.predict(array)
    #     n = np.array([2, 2])
    #     self.assertTrue(np.array_equal(predicted, n))
#!/usr/bin/python3
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
# along with Damegender; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

from nltk.corpus import names
import nltk
import csv
import unidecode
import unicodedata
import numpy as np
import configparser
import os
import re
import sys
import json

from collections import OrderedDict
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.decomposition import PCA
from app.dame_utils import DameUtils

csv.field_size_limit(3000000)

du = DameUtils()

class Gender(object):
    # That's the root class in the heritage,
    # apis classes and sexmachine is a gender
    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.config.read('config.cfg')
        self.males = 0
        self.females = 0
        self.unknown = 0

    def in_dict(self, name):
        f = os.popen('dict '+name)
        in_dict = False
        for line in f:
            if (re.match(r'[0-9]+ definitions found', line)):
                in_dict = True
        return in_dict

# FEATURES METHODS #

    def features(self, name):
        # features method created to check the nltk classifier
        features = {}
        features["first_letter"] = name[0].lower()
        features["last_letter"] = name[-1].lower()
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            features["count({})".format(letter)] = name.lower().count(letter)
            features["has({})".format(letter)] = (letter in name.lower())
        return features

    def features_int(self, name):
        # features method created to check the scikit classifiers
        features_int = {}
        features_int["first_letter"] = ord(name[0].lower())
        features_int["last_letter"] = ord(name[-1].lower())
        for letter in 'abcdefghijklmnopqrstuvwxyz':
            num = name.lower().count(letter)
            features_int["count({})".format(letter)] = num
        features_int["vocals"] = 0
        for letter1 in 'aeiou':
            for letter2 in name:
                if (letter1 == letter2):
                    features_int["vocals"] = features_int["vocals"] + 1
        features_int["consonants"] = 0
        for letter1 in 'bcdfghjklmnpqrstvwxyz':
            for letter2 in name:
                if (letter1 == letter2):
                    features_int["consonants"] = features_int["consonants"] + 1
        # FIRST LETTER
        if (name[0].lower() in 'aeiou'):
            features_int["first_letter_vocal"] = 1
        else:
            features_int["first_letter_vocal"] = 0
        if (name[0].lower() in 'bcdfghjklmnpqrstvwxyz'):
            features_int["first_letter_consonant"] = 1
        else:
            features_int["first_letter_consonant"] = 0
        # LAST LETTER
        if (name[-1].lower() in 'aeiou'):
            features_int["last_letter_vocal"] = 1
        else:
            features_int["last_letter_vocal"] = 0
        if (name[-1].lower() in 'bcdfghjklmnpqrstvwxyz'):
            features_int["last_letter_consonant"] = 1
        else:
            features_int["last_letter_consonant"] = 0
        # h = hyphen.Hyphenator('en_US')
        # features_int["syllables"] = len(h.syllables(name))
        if (name[-1].lower() == "a"):
            features_int["last_letter_a"] = 1
        else:
            features_int["last_letter_a"] = 0
        if (name[-1].lower() == "o"):
            features_int["last_letter_o"] = 1
        else:
            features_int["last_letter_o"] = 0
        return features_int

    # DATASETS METHODS #

    def ukfile(self):
        # create a file with name and prob from uk births
        total = 0
        for i in range(1880, 2018):
            # first we acquire the total of births from 1880 to 2017
            dataset = "files/names/uk/yob" + str(i) + ".txt"
            with open(dataset) as csvfile:
                sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(sexreader, None)
                totali = 0
                for row in sexreader:
                    datasetcount = row[2]
                    totali = totali + int(datasetcount)
            total = total + totali

        # now we are going to start the json file with 1880
        jsonuk = "files/names/uk/jsonuk.json"
        file = open(jsonuk, "w")
        dataset = "files/names/uk/yob1880.txt"
        with open(dataset) as csvfile:
            sexreader1 = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(sexreader1, None)
            cnt = 0
            for row in sexreader1:
                cnt = cnt + 1
        end = cnt
        lines = []
        lines.append('[')
        with open(dataset) as csvfile:
            sexreader2 = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(sexreader2, None)
            cnt = 1
            for row in sexreader2:
                lines.append('{"name": "' + row[0] + '",')
                lines.append('"gender": "' + row[1] + '",')
                if (end == cnt):
                    lines.append('"count": ' + row[2] + '}')
                    print('"count": ' + row[2] + '}')
                else:
                    lines.append('"count": ' + row[2] + '},')
                    print('"count": ' + row[2] + '},')
                cnt = cnt + 1
            lines.append(']')
        fo = open(jsonuk, "w")
        fo.writelines(lines)
        # Cerramos el archivo
        for i in range(1881, 2018):
            dataset = "files/names/uk/yob" + str(i) + ".txt"
            with open(dataset) as csvfile:
                sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(sexreader, None)
                lines = []
                for row in sexreader:
                    print(row)
                #         Cerramos el archivo
        fo.close()
        return 1

    def males_list(self, corpus='es'):
        ine_path = 'files/names/names_es/masculinos.txt'
        uy_path = 'files/names/names_uy/uymasculinos.txt'
        uk_path = 'files/names/names_uk/ukmales.txt'
        us_path = 'files/names/names_us/usmales.txt'
        m = ""
        if ((corpus == 'es') or (corpus == 'ine')):
            m = du.csvcolumn2list(ine_path)
        elif (corpus == 'uk'):
            m = du.csvcolumn2list(uk_path)
        elif (corpus == 'us'):
            m = du.csvcolumn2list(us_path)
        elif (corpus == 'uy'):
            m = du.csvcolumn2list(uy_path)
        elif (corpus == 'all'):
            m = du.csvcolumn2list(ine_path) + du.csvcolumn2list(us_path) + du.csvcolumn2list(us_path) + du.csvcolumn2list(uy_path)
            m = du.delete_duplicated(m)
        return m

    def females_list(self, corpus='es'):
        ine_path = 'files/names/names_es/femeninos.txt'
        uy_path = 'files/names/names_uy/uyfemeninos.txt'
        uk_path = 'files/names/names_uk/ukfemales.txt'
        us_path = 'files/names/names_us/usfemales.txt'
        m = ""
        if ((corpus == 'es') or (corpus == 'ine')):
            m = du.csvcolumn2list(ine_path)
        elif (corpus == 'uk'):
            m = du.csvcolumn2list(uk_path)
        elif (corpus == 'us'):
            m = du.csvcolumn2list(us_path)
        elif (corpus == 'uy'):
            m = du.csvcolumn2list(uy_path)
        elif (corpus == 'all'):
            m = du.csvcolumn2list(ine_path) + du.csvcolumn2list(us_path) + du.csvcolumn2list(us_path) + du.csvcolumn2list(uy_path)
            m = du.delete_duplicated(m)
        return m


    def csv2names(self, path='files/names/partial.csv', *args, **kwargs):
        # make a list from a csv file
        surnames = kwargs.get('surnames', False)
        header = kwargs.get('header', True)
        csvlist = []
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            if (header == True):
                next(sexreader, None)
            for row in sexreader:
                name = row[0].title()
                name = name.replace('\"', '')
                # middlename = row[1].replace(' ', '')
                # middlename = row[1].replace('\"', '')

                # if (name_and_middlename == True):
                #     name = name + " " + middlename
                #     name = name.title()

                if (surnames == True):
                    surname = row[2].title()
                    surname = row[2].replace('\"', '')
                    elem = [name, surname]
                    csvlist.append(elem)
                else:
                    csvlist.append(name)
        return csvlist


    def csv2json(self, path="", *args, **kwargs):
        # csv to json file
        surnames = kwargs.get('surnames', False)
        header = kwargs.get('header', True)
        l = kwargs.get('l', [ ]) # l is a list, such as, guess_list or gender_list
        jsonf = kwargs.get('jsonf', 'files/names/csv2json.json')
        csv2names = self.csv2names(path=path, surnames=surnames, header=header)
        string = ""
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            if (header == True):
                next(sexreader, None)
            string = '['
            i = 0
            for row in sexreader:
                name = row[0].title()
                name = name.replace('\"', '')

                middlename = row[1].replace(' ', '')
                middlename = row[1].replace('\"', '')

                lastname = row[2].title()
                lastname = row[2].replace('\"', '')

                gender = row[4]
                if surnames:
                    string = string + '{"name":"'+ name + ' ' + middlename +'", \n'
                else:
                    string = string + '{"name":"'+ name + '", \n'
                string = string + '"surname":"'+ lastname +'", \n'
                string = string + '"probability": 1, \n'
                if (l == [ ] ):
                    string = string + '"gender":"'+ gender +'"}, \n'
                elif (len(l) <= i + 1):
                    string = string + '"gender":"'+str(l[i])+'"} \n'
                else:
                    string = string + '"gender":"'+str(l[i])+'"}, \n'
                i = i + 1
            string = string + ']'
        file = open(jsonf, "w")
        file.writelines(str(string))
        file.close()


    def name2gender_in_dataset(self, name, dataset=''):
        guess = 2
        if (dataset == "names_es"):
            with open(dataset+"/"+"femeninos.txt") as csvfile:
                sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(sexreader, None)
                for row in sexreader:
                    datasetname = row.title()
                    if (datasetname == name):
                        guess = 0
            with open(dataset+"/"+"masculinos.txt") as csvfile:
                sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(sexreader, None)
                for row in sexreader:
                    datasetname = row.title()
                    if (datasetname == name):
                        guess = 1
        if (dataset == "files/names/nam_dict.txt"):
            cmd = 'grep -i "' + name
            cmd = cmd + ' " files/names/nam_dict.txt > files/logs/grep.tmp'
            os.system(cmd)
            results = [i for i in open('files/logs/grep.tmp', 'r').readlines()]
            for row in results:
                datasetname = row[1].title()
                if (datasetname == name):
                    guess = row[0].title()
                    if ((guess == 'F') | (guess == '?F')):
                        guess = 0
                    elif ((guess == 'M') | (guess == '?M')):
                        guess = 1
                    elif (guess == '='):
                        guess = 2
        if (dataset == "files/names/all.csv"):
            with open(dataset) as csvfile:
                sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(sexreader, None)
                for row in sexreader:
                    datasetname = row[0].title()
                    if (datasetname == name):
                        guess = row[4]
                        if (guess == 'm'):
                            guess = 1
                        elif (guess == 'f'):
                            guess = 0
                        elif (guess == 'u'):
                            guess = 2
        if (dataset == "files/names/yob2017.txt"):
            with open(dataset) as csvfile:
                sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(sexreader, None)
                for row in sexreader:
                    datasetname = row[0].title()
                    if (datasetname == name):
                        guess = row[1]
                        if (guess == 'M'):
                            guess = 1
                        elif (guess == 'F'):
                            guess = 0
        return guess

    def dataset2genderlist(self, dataset=''):
        genderlist = []
        path_all = "files/names/all.csv"
        path_allnoun = "files/names/allnoundefined.csv"
        if ((dataset == path_all) or (dataset == path_allnoun)):
            with open(dataset) as csvfile:
                sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(sexreader, None)
                for row in sexreader:
                    datasetname = row[0].title()
                    guess = row[4]
                    guess = guess.replace('\"', '')
                    if (guess == 'm'):
                        guess = 1
                    elif (guess == 'f'):
                        guess = 0
                    elif (guess == 'u'):
                        guess = 2
                    genderlist.append(guess)
        if (dataset == "files/names/yob2017.txt"):
            with open(dataset) as csvfile:
                sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
                next(sexreader, None)
                for row in sexreader:
                    datasetname = row[0].title()
                    guess = row[1]
                    guess = guess.replace('\"', '')
                    if (guess == 'M'):
                        guess = 1
                    elif (guess == 'F'):
                        guess = 0
                    genderlist.append(guess)
        return genderlist


    def name_frec(self, name, *args, **kwargs):
        # guess list method
        dataset = kwargs.get('dataset', 'es')

        du = DameUtils()
        name = du.drop_accents(name)
        path_males = 'files/names/names_es/esmasculinos.csv'
        if ((dataset == 'ine') or (dataset == 'es')):
            path_males = 'files/names/names_es/esmasculinos.csv'
        elif (dataset == 'uy'):
            path_males = 'files/names/names_uy/uymasculinos.csv'
        elif (dataset == 'uk'):
            path_males = 'files/names/names_uk/ukmales.csv'
        elif (dataset == 'us'):
            path_males = 'files/names/names_us/usmales.csv'
        file_males = open(path_males, 'r')
        readerm = csv.reader(file_males, delimiter=',', quotechar='|')
        males = 0
        for row in readerm:
            if ((len(row) > 1) and (row[0].lower() == name.lower())):
                males = row[1]
                males = du.drop_dots(males)
        path_females = 'files/names/names_es/esfemeninos.csv'
        if ((dataset == 'ine') or (dataset == 'es')):
            path_females = 'files/names/names_es/esfemeninos.csv'
        elif (dataset == 'uy'):
            path_females = 'files/names/names_uy/uyfemeninos.csv'
        elif (dataset == 'uk'):
            path_females = 'files/names/names_uk/ukfemales.csv'
        elif (dataset == 'us'):
            path_females = 'files/names/names_us/usfemales.csv'

        file_females = open(path_females, 'r')
        readerf = csv.reader(file_females, delimiter=',', quotechar='|')
        females = 0
        for row in readerf:
            if ((len(row) > 1) and (row[0].lower() == name.lower())):
                females = row[1]
                females = du.drop_dots(females)
        dicc = {"females": females, "males": males}

        return dicc

    def namdict2file(self):
        filepath = 'files/names/nam_dict.txt'
        mylist = []
        with open(filepath) as fp:
            for cnt, line in enumerate(fp):
                # From 3 to 25
                if (cnt > 292):
                    name = ""
                    for i in range(3, 25):
                        name = name + str(line[i])
                    mylist += [name]
        file = open("files/names/nam_dict_list.txt", "w")
        file.writelines(mylist)
        file.close()

    def filenamdict2list(self):
        names = []
        dataset = 'files/names/nam_dict_list.txt'
        with open(dataset, 'r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                names = names + row[0].split()
        return names

# GUESS #

    def guess(self, name, binary=False, *args, **kwargs):
        # guess list method
        dataset = kwargs.get('dataset', 'es')
        # guess method to check names dictionary
        guess = ''
        name = unidecode.unidecode(name).title()
        name.replace(name, "")
        dicc = self.name_frec(name, dataset)
        m = int(dicc['males'])
        f = int(dicc['females'])
        if (m > f):
            if binary:
                guess = 1
            else:
                guess = "male"
        elif (f > m):
            if binary:
                guess = 0
            else:
                guess = "female"
        else:
            if binary:
                guess = 2
            else:
                guess = "unknown"
        return guess

    def guess_list(self, path='files/names/partial.csv', binary=False, *args, **kwargs):
        # guess list method
        header = kwargs.get('header', True)
        slist = []
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            if (header == True):
                next(sexreader, None)
            for row in sexreader:
                name = row[0].title()
                name = name.replace('\"', '')
                slist.append(self.guess(name, binary))
        return slist

    def gender_list(self, path, *args, **kwargs):
        # counting males, females and unknown
        header = kwargs.get('header', True)
        glist = []
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            if (header == True):
                next(sexreader, None)
            count_females = 0
            count_males = 0
            count_unknown = 0
            gender = ""
            for row in sexreader:
                if (row[4] != ""):
                    gender = row[4]
                if (gender == 'f'):
                    g = 0
                    count_females = count_females + 1
                elif (gender == 'm'):
                    g = 1
                    count_males = count_males + 1
                else:
                    g = 2
                    count_unknown = count_unknown + 1
                glist.append(g)
        self.females = count_females
        self.males = count_males
        self.unknown = count_unknown
        return glist


    def pretty_gg_list(self, path, jsonf, *args, **kwargs):
        measure = kwargs.get('measure', 'accuracy')
        binary = kwargs.get('binary', True)
        ml = kwargs.get('ml', 'nltk')
        api = kwargs.get('api', 'damegender')
        header = kwargs.get('header', True)
        gl = self.gender_list(path=path)

        if (os.path.isfile(jsonf)):
            if (self.json_eq_csv_in_names(jsonf=jsonf, path=path)):
                print("################### "+ api +"!!")
                print("Gender list: " + str(gl))
                sl = self.json2guess_list(jsonf=jsonf, binary=True)
                print("Guess list:  " +str(sl))
                self.print_measures(gl, sl, measure, api)
            else:
                print("Names in json and csv are differents")
                print("%s names in csv" % len(self.csv2names(path=path, header=header)))
                print("%s names in json" % len(self.json2names(jsonf=jsonf, surnames=False)))
                v = self.first_uneq_json_and_csv_in_names(jsonf=jsonf, path=path)
                print("The first position finding unmatched names is %s and the name is %s" % (v[1], v[0]))
                print("Names in csv: %s:" % self.csv2names(path=path, header=header))
                print("Names in json: %s:" % self.json2names(jsonf=jsonf, surnames=False))
        else:
            print("In the path %s doesn't exist file" % jsonf)
            print("You can create one, but this process can take long time")
            yes_or_not = du.yes_or_not("Do you want create a json file? ")
            if yes_or_not:
                sl = self.guess_list(path=path, binary=binary, ml=ml)
                self.csv2json(path=path, l=sl, jsonf=jsonf)
                if (self.json_eq_csv_in_names(jsonf=jsonf, path=args.csv)):
                    print("################### "+ api +"!!")
                    print("Gender list: " + str(gl))
                    print("Guess list:  " +str(sl))
                    self.print_measures(gl, sl, measure, api)
                else:
                    print("Names in json and csv are differents")
                    print("Names in csv: %s:" % self.csv2names(path=path, header=header))
                    print("Names in json: %s:" % self.json2names(jsonf=jsonf, surnames=False))
        return 1

    def pretty_cm(self, path, jsonf, *args, **kwargs):
        api = kwargs.get('api', 'damegender')
        reverse = kwargs.get('reverse', False)
        dimensions = kwargs.get('dimensions', '3x2')
        gl = self.gender_list(path=path)
#        dna = DameNameapi()
        print("%s confusion matrix:\n" % api)
        #    dna.print_confusion_matrix_gender(path=args.csv, dimensions=args.dimensions)
        if (os.path.isfile(jsonf)):
            self.print_confusion_matrix_gender(path=path, dimensions=dimensions, jsonf=jsonf, reverse=reverse)
        elif (args.jsondownloaded == ''):
            self.print_confusion_matrix_gender(path=path, dimensions=dimensions, reverse=reverse)
        else:
            print("In the path %s doesn't exist file" % jsonf)



# METHODS ABOUT STATISTICS #

    def count_true2guess(self, truevector, guessvector, true, guess):
        i = 0
        count = 0
        if (len(truevector) >= len(guessvector)):
            maxi = len(guessvector)
        else:
            maxi = len(truevector)
        while (i < maxi):
            if ((truevector[i] == true) and (guessvector[i] == guess)):
                count = count + 1
            i = i + 1
        return count

    def femalefemale(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 0, 0)

    def femalemale(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 0, 1)

    def femaleundefined(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 0, 2)

    def malefemale(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 1, 0)

    def malemale(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 1, 1)

    def maleundefined(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 1, 2)

    def undefinedfemale(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 2, 0)

    def undefinedmale(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 2, 1)

    def undefinedundefined(self, truevector, guessvector):
        return self.count_true2guess(truevector, guessvector, 2, 2)

    def accuracy_score_dame(self, truevector, guessvector):
        if (len(truevector) == len(guessvector)):
            divider = self.femalefemale(truevector, guessvector)
            divider = divider + self.malemale(truevector, guessvector)
            dividend = self.femalefemale(truevector, guessvector)
            dividend = dividend + self.malemale(truevector, guessvector)
            dividend = dividend + self.malefemale(truevector, guessvector)
            dividend = dividend + self.femalemale(truevector, guessvector)
            dividend = dividend + self.femaleundefined(truevector, guessvector)
            dividend = dividend + self.maleundefined(truevector, guessvector)
            result = divider / dividend
        else:
            result = 0
            print("Both vectors must have the same length")
            print("truevector length: %s" % len(truevector))
            print("guessvector length: %s" % len(guessvector))
            print("truevector: %s" % truevector)
            print("guessvector: %s" % guessvector)
        return result

    def accuracy(self, path):
        gl = self.gender_list(path)
        sl = self.guess_list(path, binary=True)
        return self.accuracy_score_dame(gl, sl)


    def precision(self, truevector, guessvector):
        result = 0
        divider = self.femalefemale(truevector, guessvector)
        divider = divider + self.malemale(truevector, guessvector)
        dividend = self.femalefemale(truevector, guessvector)
        dividend = dividend + self.malemale(truevector, guessvector)
        dividend = dividend + self.malefemale(truevector, guessvector)
        result = divider / dividend
        return result

    def recall(self, truevector, guessvector):
        result = 0
        divider = self.femalefemale(truevector, guessvector)
        divider = divider + self.malemale(truevector, guessvector)
        dividend = self.femalefemale(truevector, guessvector)
        dividend = dividend + self.malemale(truevector, guessvector)
        dividend = dividend + self.malefemale(truevector, guessvector)
        dividend = dividend + self.femaleundefined(truevector, guessvector)
        dividend = dividend + self.maleundefined(truevector, guessvector)
        result = divider / dividend
        return result

    def f1score(self, truevector, guessvector):
        result = 0
        divider = self.precision(truevector, guessvector)
        divider = divider * self.recall(truevector, guessvector)
        dividend = self.precision(truevector, guessvector)
        dividend = dividend + self.recall(truevector, guessvector)
        result = 2 * (divider / dividend)
        return result

    def error_coded(self, truevector, guessvector):
        result = 0
        divider = self.femalemale(truevector, guessvector)
        divider = divider + self.malefemale(truevector, guessvector)
        divider = divider + self.maleundefined(truevector, guessvector)
        divider = divider + self.femaleundefined(truevector, guessvector)
        dividend = self.malemale(truevector, guessvector)
        dividend = dividend + self.femalemale(truevector, guessvector)
        dividend = dividend + self.malefemale(truevector, guessvector)
        dividend = dividend + self.femalefemale(truevector, guessvector)
        dividend = dividend + self.maleundefined(truevector, guessvector)
        dividend = dividend + self.femaleundefined(truevector, guessvector)
        result = divider / dividend
        return result

    def error_coded_without_na(self, truevector, guessvector):
        result = 0
        divider = self.femalemale(truevector, guessvector)
        divider = divider + self.malefemale(truevector, guessvector)
        dividend = self.malemale(truevector, guessvector)
        dividend = dividend + self.femalemale(truevector, guessvector)
        dividend = dividend + self.malefemale(truevector, guessvector)
        dividend = dividend + self.femalefemale(truevector, guessvector)
        result = divider / dividend
        return result

    def na_coded(self, truevector, guessvector):
        result = 0
        divider = self.maleundefined(truevector, guessvector)
        divider = divider + self.femaleundefined(truevector, guessvector)
        dividend = self.malemale(truevector, guessvector)
        dividend = dividend + self.femalemale(truevector, guessvector)
        dividend = dividend + self.malefemale(truevector, guessvector)
        dividend = dividend + self.femalefemale(truevector, guessvector)
        dividend = dividend + self.maleundefined(truevector, guessvector)
        dividend = dividend + self.femaleundefined(truevector, guessvector)
        result = divider / dividend
        return result

    def error_gender_bias(self, truevector, guessvector):
        divider = self.malefemale(truevector, guessvector)
        divider = divider - self.femalemale(truevector, guessvector)
        dividend = self.malemale(truevector, guessvector)
        dividend = dividend + self.femalemale(truevector, guessvector)
        dividend = dividend + self.malefemale(truevector, guessvector)
        dividend = dividend + self.femalefemale(truevector, guessvector)
        result = divider / dividend
        return result

    def weighted_error(self, truevector, guessvector, w):
        divider = self.femalemale(truevector, guessvector)
        divider = divider + self.malefemale(truevector, guessvector)
        dot = self.maleundefined(truevector, guessvector)
        dot = dot + self.femaleundefined(truevector, guessvector)
        divider = divider + w * dot
        dividend = self.malemale(truevector, guessvector)
        dividend = dividend + self.femalemale(truevector, guessvector)
        dividend = dividend + self.malefemale(truevector, guessvector)
        dividend = dividend + self.femalefemale(truevector, guessvector)
        dot = self.maleundefined(truevector, guessvector)
        dot = dot + self.femaleundefined(truevector, guessvector)
        dividend = dividend + w * dot
        result = divider / dividend
        return result


    def confusion_matrix(self, path='files/names/partial.csv'):
        # this method is using scikit library (deprecated)
        gl = self.gender_list(path)
        sl = self.guess_list(path, binary=True)
        return confusion_matrix(gl, sl)

    def confusion_matrix_table(self, truevector, guessvector):
        # this method returns a 3x3 confusion matrix as python vectors

        # femalefemale
        self.ff = self.count_true2guess(truevector, guessvector, 0, 0)
        # femalemale
        self.fm = self.count_true2guess(truevector, guessvector, 0, 1)
        # femaundefined
        self.fu = self.count_true2guess(truevector, guessvector, 0, 2)
        # malefemale
        self.mf = self.count_true2guess(truevector, guessvector, 1, 0)
        # malemale
        self.mm = self.count_true2guess(truevector, guessvector, 1, 1)
        # maleundefined
        self.mu = self.count_true2guess(truevector, guessvector, 1, 2)
        # undefinedfemale
        self.uf = self.count_true2guess(truevector, guessvector, 1, 0)
        # undefinedmale
        self.um = self.count_true2guess(truevector, guessvector, 1, 1)
        # undefinedundefined
        self.uu = self.count_true2guess(truevector, guessvector, 1, 2)

        l = [[self.ff, self.fm, self.fu],
             [self.mf, self.mm, self.mu],
             [self.uf, self.um, self.uu]]

        res = [[l[0][0], l[0][1], l[0][2]],
               [l[1][0], l[1][1], l[1][2]],
               [l[2][0], l[2][1], l[2][2]]]
        return res

    def confusion_matrix_gender(self, path='', jsonf=''):
        # this method is an interfaz to confusion_matrix_table allowing introduce a json file
        # in dame_sexmachine we must rewrite it to allow machine learning algorithm
        truevector = self.gender_list(path)
        if (os.path.isfile(jsonf)):
            guessvector = self.json2guess_list(jsonf=jsonf, binary=True)
        else:
            guessvector = self.guess_list(path, binary=True)
        res = self.confusion_matrix_table(truevector, guessvector)
        return res

    def print_confusion_matrix_gender(self, path='', dimensions='', *args, **kwargs):
        reverse = kwargs.get('reverse', False)
        jsonf = kwargs.get('jsonf', '')
        jf = os.getcwd() + "/" +  jsonf
        if (os.path.isfile(jf)):
            cmd = self.confusion_matrix_gender(path, jsonf=jf)
        else:
            cmd = self.confusion_matrix_gender(path)
        if (dimensions == "1x1"):
            if (reverse == False):
                print("[[ %s ]]" % (cmd[1][1]))
            elif (reverse == True):
                print("[[ %s ]]" % (cmd[0][0]))
        elif (dimensions == "1x2"):
            if (reverse == False):
                print("[[ %s, %s ]]" % (cmd[1][1], cmd[1][0]))
            elif (reverse == True):
                print("[[ %s, %s ]]" % (cmd[0][0], cmd[0][1]))
        elif (dimensions == "1x3"):
            if (reverse == False):
                print("[[ %s, %s, %s ]]" % (cmd[1][1], cmd[1][0], cmd[1][2]))
            elif (reverse == True):
                print("[[ %s, %s, %s ]]" % (cmd[0][0], cmd[0][1], cmd[0][2]))
        elif (dimensions == "2x1"):
            if (reverse == False):
                print("[[ %s ]" % (cmd[1][1]))
                print(" [ %s ]]" % (cmd[1][0]))
            elif (reverse == True):
                print("[[ %s ]" % (cmd[0][0]))
                print(" [ %s ]]" % (cmd[0][1]))
        elif (dimensions == "2x2"):
            if (reverse == False):
                print("[[ %s , %s ]" % (cmd[1][1], cmd[1][0]))
                print(" [ %s , %s ]]" % (cmd[0][1], cmd[0][0]))
            if (reverse == True):
                print("[[ %s , %s ]" % (cmd[0][0], cmd[0][1]))
                print(" [ %s , %s ]]" % (cmd[1][0], cmd[1][1]))
        elif (dimensions == "2x3"):
            if (reverse == False):
                print("[[ %s, %s, %s ]" % (cmd[1][1], cmd[1][0], cmd[1][2]))
                print(" [ %s, %s, %s ]]" % (cmd[0][1], cmd[0][0], cmd[0][2]))
            if (reverse == True):
                print("[[ %s, %s, %s ]" % (cmd[0][0], cmd[0][1], cmd[0][2]))
                print(" [ %s, %s, %s ]]" % (cmd[1][0], cmd[1][1], cmd[1][2]))
        elif (dimensions == "3x1"):
            if (reverse == False):
                print("[[ %s ]" % (cmd[1][1]))
                print(" [ %s ]" % (cmd[0][1]))
                print(" [ %s ]]" % (cmd[2][1]))
            elif (reverse == True):
                print("[[ %s ]," % (cmd[0][0]))
                print(" [ %s ]" % (cmd[1][0]))
                print(" [ %s ]]" % (cmd[2][0]))
        elif (dimensions == "3x2"):
            if (reverse == False):
                print("[[ %s , %s ]" % (cmd[1][1], cmd[1][0]))
                print(" [ %s , %s ]" % (cmd[0][1], cmd[0][0]))
                print(" [ %s , %s ]]" % (cmd[2][1], cmd[2][0]))
            if (reverse == True):
                print("[[ %s, %s ]" % (cmd[0][0], cmd[0][1]))
                print(" [ %s, %s ]" % (cmd[1][0], cmd[1][1]))
                print(" [ %s, %s ]]" % (cmd[2][0], cmd[2][1]))
        elif (dimensions == "3x3"):
            if (reverse == False):
                print("[[ %s, %s, %s ]" % (cmd[1][1], cmd[1][0], cmd[1][2]))
                print(" [ %s, %s, %s ]" % (cmd[0][1], cmd[0][0], cmd[0][2]))
                print(" [ %s, %s, %s ]]" % (cmd[2][1], cmd[2][0], cmd[2][2]))
            if (reverse == True):
                print("[[ %s, %s, %s ]" % (cmd[0][0], cmd[0][1], cmd[0][2]))
                print(" [ %s, %s, %s ]" % (cmd[1][0], cmd[1][1], cmd[1][2]))
                print(" [ %s, %s, %s ]]" % (cmd[2][0], cmd[2][1], cmd[2][2]))
        return ""


    def features_list(self, path='files/names/partial.csv', sexdataset=''):
        flist = []
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(sexreader, None)
            for row in sexreader:
                name = row[0].title()
                name = name.replace('\"', '')
                flist.append(list(self.features_int(name).values()))
        return flist

    def features_list_categorical(self, path='files/names/partial.csv'):
        flist = []
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(sexreader, None)
            for row in sexreader:
                name = row[0].title()
                name = name.replace('\"', '')
                l = list([self.features_int(name)["first_letter"],
                          self.features_int(name)["last_letter"],
                          self.features_int(name)["last_letter_a"],
                          self.features_int(name)["first_letter_vocal"],
                          self.features_int(name)["last_letter_vocal"],
                          self.features_int(name)["last_letter_consonant"]])
                flist.append(l)
        return flist

    def features_list_no_categorical(self, path='files/names/partial.csv'):
        flist = []
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(sexreader, None)
            for row in sexreader:
                name = row[0].title()
                name = name.replace('\"', '')
                l = list([self.features_int(name)["count(a)"],
                          self.features_int(name)["count(b)"],
                          self.features_int(name)["count(c)"],
                          self.features_int(name)["count(d)"],
                          self.features_int(name)["count(e)"],
                          self.features_int(name)["count(f)"],
                          self.features_int(name)["count(g)"],
                          self.features_int(name)["count(h)"],
                          self.features_int(name)["count(i)"],
                          self.features_int(name)["count(j)"],
                          self.features_int(name)["count(k)"],
                          self.features_int(name)["count(l)"],
                          self.features_int(name)["count(m)"],
                          self.features_int(name)["count(n)"],
                          self.features_int(name)["count(o)"],
                          self.features_int(name)["count(p)"],
                          self.features_int(name)["count(q)"],
                          self.features_int(name)["count(r)"],
                          self.features_int(name)["count(s)"],
                          self.features_int(name)["count(t)"],
                          self.features_int(name)["count(u)"],
                          self.features_int(name)["count(v)"],
                          self.features_int(name)["count(w)"],
                          self.features_int(name)["count(x)"],
                          self.features_int(name)["count(y)"],
                          self.features_int(name)["count(z)"],
                          self.features_int(name)["vocals"],
                          self.features_int(name)["consonants"]])
                flist.append(l)
        return flist

    def features_list_no_letters(self, path='files/names/partial.csv'):
        flist = []
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(sexreader, None)
            for row in sexreader:
                name = row[0].title()
                name = name.replace('\"', '')
                l = list([self.features_int(name)["first_letter"],
                          self.features_int(name)["last_letter"],
                          self.features_int(name)["vocals"],
                          self.features_int(name)["consonants"],
                          self.features_int(name)["first_letter_vocal"],
                          self.features_int(name)["last_letter_vocal"],
                          self.features_int(name)["first_letter_consonant"],
                          self.features_int(name)["last_letter_consonant"],
                          self.features_int(name)["last_letter_a"],
                          self.features_int(name)["last_letter_o"]])
                flist.append(l)
        return flist

    def features_list_no_undefined(self, path=''):
        flist = []
        with open(path) as csvfile:
            sexreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            next(sexreader, None)
            for row in sexreader:
                name = row[0].title()
                name = name.replace('\"', '')
                g = row[4].replace('\"', '')
                if ((g == "m") | (g == "f")):
                    flist.append(list(self.features_int(name).values()))
        return flist

    def features_list2csv(self, path, categorical="both"):
        if (categorical == "categorical"):
            fl = self.features_list_categorical(path)
            first_line = "first_letter, last_letter, last_letter_a, " \
                         "first_letter_vocal, last_letter_vocal, " \
                         "last_letter_consonant"
            f = open('files/features_list_cat.csv', 'w')
        elif (categorical == "nocategorical"):
            fl = self.features_list_no_categorical(path)
            first_line = "a, b, c, d, e, f, g, h, i, j, k, l, m, " \
                         "n, o, p, q, r, s, t, u, v, w, x, y, z, " \
                         "vocals, consonants"
            f = open('files/features_list_no_cat.csv', 'w')
        elif (categorical == "noletters"):
            fl = self.features_list_no_letters(path)
            first_line = "first_letter, last_letter, vocals, " \
                         "consonants, first_letter_vocal," \
                         "last_letter_vocal, first_letter_consonant, " \
                         "last_letter_consonant," \
                         "last_letter_a, last_letter_o"
            f = open('files/features_list_no_letters.csv', 'w')
        elif (categorical == "noundefined"):
            fl = self.features_list_no_undefined(path)
            first_line = "first_letter, last_letter, a, b, c, d, e, " \
                         "f, g, h, i, j, k, l, m, n, o, p, q, r, s, " \
                         "t, u, v, w, x, y, z, vocals, consonants, " \
                         "first_letter_vocal, last_letter_vocal, " \
                         "first_letter_consonant, last_letter_consonant, " \
                         "last_letter_a, last_letter_o"
            f = open('files/features_list_no_undefined.csv', 'w')
        else:
            fl = self.features_list(path)
            first_line = "first_letter, last_letter, a, b, c, d, e, f, " \
                         "g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, " \
                         "v, w, x, y, z, vocals, consonants, " \
                         "first_letter_vocal, last_letter_vocal, " \
                         "first_letter_consonant, last_letter_consonant, " \
                         "last_letter_a, last_letter_o"
            f = open('files/features_list.csv', 'w')
        f.write(first_line+"\n")
        for i in fl:
            line = ""
            count = 0
            while (count < (len(i) - 1)):
                line = line + str(i[count]) + ", "
                count = count + 1
            f.write(line+str(i[count])+"\n")
        f.close()

    def pca(self, path='files/names/partial.csv', n=2):
        X = np.array(self.features_list())
        pca = PCA(n_components=n)
        return pca.fit(X)

    # def print_envolve_measures
    #     if (ds.json_eq_csv_in_names(jsonf=args.jsondownloaded, path=args.csv)):
    #         print("################### Damegender!!")
    #         print("Gender list: " + str(gl))
    #         sl = ds.json2guess_list(jsonf=args.jsondownloaded, binary=True)
    #         print("Guess list:  " +str(sl))
    #         ds.print_measures(gl, sl, args.measure, "Damegender")
    #     else:
    #         print("Names in json and csv are differents")
    #         print("Names in csv: %s:" % ds.csv2names(path=args.csv))
    #         print("Names in json: %s:" % ds.json2names(jsonf=args.jsondownloaded, surnames=False))


    def print_measures(self, gl1, gl2, measure, api_name):
        if (measure == "accuracy"):
            gender_accuracy = self.accuracy_score_dame(gl1, gl2)
            print("%s accuracy: %s" % (api_name, gender_accuracy))

        elif (measure == "precision"):
            gender_precision = self.precision(gl1, gl2)
            print("%s precision: %s" % (api_name, gender_precision))

        elif (measure == "recall"):
            gender_recall = self.recall(gl1, gl1)
            print("%s recall: %s" % (api_name, gender_recall))
        elif (measure == "f1score"):
            gender_f1score = self.f1score(gl1, gl2)
            print("%s f1score: %s" % (api_name, gender_f1score))

    def json2guess_list(self, jsonf="", binary=False):
        jsondata = open(jsonf).read()
        json_object = json.loads(jsondata)
        guesslist = []

        for i in json_object:
            if binary:
                if ((i['gender'] == 'female') or (i['gender'] == 'f') or (i['gender'] == 0)):
                    guesslist.append(0)
                elif ((i['gender'] == 'male') or (i['gender'] == 'm') or (i['gender'] == 1)):
                    guesslist.append(1)
                else:
                    guesslist.append(2)
            else:
                guesslist.append(i['gender'])
        return guesslist


    def json2names(self, jsonf="", surnames=False):
        jsondata = open(jsonf).read()
        json_object = json.loads(jsondata)
        nameslist = []
        for i in json_object:
            if (i["name"] != ''):
                if (surnames == True):
                    nameslist.append([i["name"], i["surname"]])
                else:
                    nameslist.append(i["name"])
        return nameslist


    def json_eq_csv_in_names(self, jsonf="", path="", *args, **kwargs):
        header = kwargs.get('header', True)
        boolean = False
        json = self.json2names(jsonf=jsonf, surnames=False)
        json_lower = [element.lower() for element in json] ; json
        csv = self.csv2names(path=path, header=header)
        csv_lower = [element.lower() for element in csv] ; csv
        count = 0
        i = 0
        maxi = len(json_lower) -1
        if (maxi < len(csv_lower)):
            maxi = len(csv_lower) -1
        while (maxi > i):
            if (json_lower[i] == csv_lower[i]):
                count = count +1
            i = i+1
        boolean = ((len(json_lower) == len(csv_lower)) and ((len(json_lower) -1) == count))
        return boolean

    def first_uneq_json_and_csv_in_names(self, jsonf="", path="", *args, **kwargs):
        header = kwargs.get('header', True)
        json = self.json2names(jsonf=jsonf, surnames=False)
        csv = self.csv2names(path=path, header=header)
        i = 0
        maxi_json = len(json) -1
        maxi_csv = len(csv) - 1
        while ((i < maxi_json) and (i < maxi_csv) and (json[i].lower() == csv[i].lower())):
            i = i + 1
        ret = json[i].lower()
        if ((i > maxi_json) and (i > maxi_csv)):
            ret = ""
        elif (i > maxi_json):
            ret = csv[i].lower()
        elif (i > maxi_csv):
            ret = json[i].lower()
        return [ret, i]

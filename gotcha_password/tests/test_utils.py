from django.test import TestCase

import string, random

from base.utils import *

class UtilitiesTestCase(TestCase):
    def test_get_random_seed(self):
        seed1 = get_random_seed()
        seed2 = get_random_seed()
        self.assertNotEqual(seed1, seed2)

    def test_make_password(self):
        raw_password = 'password'
        labels = [char for char in string.ascii_lowercase]
        password, permutation1 = make_password(raw_password, labels)

        self.assertEqual(len(password.split('$')), 2)

        _, permutation2 = make_password(raw_password, labels)
        self.assertNotEqual(permutation1, permutation2)

    def test_hash_password(self):
        raw_password = 'password'
        seed = get_random_seed()
        permutation = range(10)
        self.assertEqual(
            hash_password(raw_password, seed, permutation),
            hash_password(raw_password, seed, permutation),
        )

    def test_list_permutations(self):
        permutation = [0, 1, 2]
        diffs = list(list_permutations(permutation, 0))
        self.assertEqual(len(diffs), 1)
        self.assertEqual(diffs[0], permutation)

        diffs = list(list_permutations(permutation, 2))
        self.assertEqual(diffs, [
            [0,1,2], [1,0,2], [2,1,0], [0,2,1]
        ])

        diffs = list_permutations([1,1,1], 2)
        for diff in diffs:
            # check no duplicates
            self.assertEqual(len(set(diff)), len(diff))


    def test_extract(self):
        raw_password = 'password'
        seed = get_random_seed()
        extract1 = extract(raw_password, seed)
        extract2 = extract(raw_password, seed)
        self.assertEqual(extract1, extract2)

    def test_generate_images(self):
        # test that future random calls are still random after calling
        seed = get_random_seed()
        generate_images(1, seed)
        val1 = random.random()
        generate_images(1, seed)
        val2 = random.random()
        self.assertNotEqual(val1, val2)

    def test_extract_labels(self):
        data = {
            'label-2': '1',
            'label-0': '2',
            'label-1': '0',
        }
        extracted = extract_labels(data)
        self.assertEqual(extracted, ['2', '0', '1'])

    def test_encode_decode(self):
        val = 'myRand0mPa$$word'
        self.assertEqual(val, decode(encode(val)))

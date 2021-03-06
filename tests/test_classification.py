""" Tests of classification process. """

import unittest

import numpy as np
import cv2 as cv

from ana_classification import ConvNetCellClassifier, NegClassifier, preprocess


class TestClassification(unittest.TestCase):

    def setUp(self):
        self.cell_classifier = ConvNetCellClassifier()
        self.neg_classifier = NegClassifier()

    def test_cnn_classes(self):
        self.assertListEqual(['HOM', 'ACA', 'NUC'], self.cell_classifier.classes)

    def test_cnn_middle_crop(self):
        img = np.random.randint(0, 255, (100, 10))
        img_cropped = self.cell_classifier._middle_crop(img)
        self.assertTupleEqual((10, 10), img_cropped.shape)
        self.assertTrue(np.all(img[45:55, :] == img_cropped))

        img = np.random.randint(0, 255, (10, 100))
        img_cropped = self.cell_classifier._middle_crop(img)
        self.assertTupleEqual((10, 10), img_cropped.shape)
        self.assertTrue(np.all(img[:, 45:55] == img_cropped))

        img = np.random.randint(0, 255, (100, 100))
        img_cropped = self.cell_classifier._middle_crop(img)
        self.assertTupleEqual(img.shape, img_cropped.shape)
        self.assertTrue(np.all(img == img_cropped))

    def test_cnn_preprocess(self):
        img = np.random.randint(0, 255, (100, 73)).astype('uint8')
        img_processed = self.cell_classifier._preprocess(img)

        self.assertTupleEqual((96, 96, 1), img_processed.shape)
        self.assertTrue(np.all(img_processed >= 0.0))
        self.assertTrue(np.all(img_processed <= 1.0))

    def test_cnn_classify(self):
        images = [np.random.rand(100, 100) for _ in range(3)]
        results = self.cell_classifier.classify(images)

        self.assertTupleEqual((3, 3), results.shape)
        self.assertTrue(np.all(results >= 0))
        self.assertTrue(np.allclose(results.sum(axis=1), np.ones((1, 3))))

    def test_neg_classify(self):
        for f in ['resources/NEG-1.tif', 'resources/NEG-2.tif', 'resources/NEG-3.tif']:
            img = preprocess(cv.imread(f), normalize=False)
            self.assertTrue(self.neg_classifier.is_negative(img), f)

        for f in ['resources/NUC-1.tif', 'resources/ACA-2.tif', 'resources/HOM-3.tif']:
            img = preprocess(cv.imread(f), normalize=False)
            self.assertFalse(self.neg_classifier.is_negative(img), f)

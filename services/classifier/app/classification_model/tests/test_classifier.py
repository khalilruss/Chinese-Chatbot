from torch import tensor
from numpy.testing import assert_equal
from unittest.mock import patch

def test_WordLevelClassifier_encode():
    from classification_model.word_level_classifier import WordLevelClassifier
    classifier = WordLevelClassifier()
    encodings =classifier.encode('你')
    assert_equal(encodings['input_ids'].numpy(), [[101, 872, 102,   0,   0,   0]])
    assert_equal(encodings['attention_mask'].numpy(), [[1, 1, 1, 0, 0, 0]])

def test_WordLevelClassifier_preprocess():
    from classification_model.word_level_classifier import WordLevelClassifier
    classifier = WordLevelClassifier()
    words = classifier.preprocess('你好吗？')
    assert words == ['你','好','吗']

def test_WordLevelClassifier_classify():
    with patch('classification_model.word_level_classifier.parser') as mock:
        mock.word_tokenize.return_value =["你", "好"]
        from classification_model.word_level_classifier import WordLevelClassifier

        classifier = WordLevelClassifier()
        classifications = classifier.classify('你好')
        assert classifications ==[{"word": "你", "level": 1}, {"word": "好", "level": 1}]
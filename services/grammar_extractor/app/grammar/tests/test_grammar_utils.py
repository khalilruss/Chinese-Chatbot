from unittest.mock import patch

def test_parseSentence():
    with patch('grammar.grammarUtils.parser') as mock:
        mock.pos_tag.return_value = [
            ('我', 'PN'), ('没有', 'VE'), ('问题', 'NN'), ('。', 'PU')]
        from grammar.grammarUtils import parseSentence
        pos_sent = parseSentence("我没有问题。")
        assert pos_sent == "我PN没有VE问题NN。PU"

def test_extractGrammar_single_pattern():
    with patch('grammar.grammarUtils.parser') as mock:
        mock.pos_tag.return_value = [('太', 'AD'), ('好', 'VA'), ('了', 'SP')]
        from grammar.grammarUtils import extractGrammar
        grammarExtracted, _ = extractGrammar("太好了")
        assert grammarExtracted == [{'rule': '太 + Adj. + 了', 'level': 1}]

def test_extractGrammar_multiple_patterns():
    with patch('grammar.grammarUtils.parser') as mock:
        mock.pos_tag.return_value = [
            ('我', 'PN'), ('没有', 'VE'), ('问题', 'NN'), ('。', 'PU')]
        from grammar.grammarUtils import extractGrammar
        grammarExtracted, _ = extractGrammar("我没有问题。")
        assert grammarExtracted == [
            {'rule': '没有/没 (+ Obj.)', 'level': 1},
            {'rule': 'Subj. + Verb (+ Obj.) ', 'level': 1}]

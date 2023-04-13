from chatbot_utils.sentence_simlarity import compare_to_history, compare_sentences, get_random_question
from transformers import  BertTokenizer
from unittest.mock import patch

MODEL_CHECKPOINT = './chatbot_utils/chatbot_model/'
tokenizer = BertTokenizer.from_pretrained(MODEL_CHECKPOINT, do_lower_case=True)

def test_compare_to_history():
    sent1 = tokenizer.convert_tokens_to_ids(tokenizer.tokenize('我很高兴'))
    results = compare_to_history([sent1],'我 很 高 兴',tokenizer)
    assert results == {'possible_out_text': '我 很 高 兴', 
                        'prev_texts': ['我 很 高 兴'], 'similarities': [1.0]}

def test_compare_sentences():
    sent1 = tokenizer.convert_tokens_to_ids(tokenizer.tokenize('我很高兴'))
    prev_text, similarity = compare_sentences('我 很 高 兴', sent1,tokenizer)
    assert similarity == 1.0

def test_get_random_question():
    with patch('chatbot_utils.sentence_simlarity.questions', ['你怎么样？']):
        sent1 = tokenizer.convert_tokens_to_ids(tokenizer.tokenize('我很高兴'))
        history, out_text = get_random_question([sent1],tokenizer)
        assert history ==[[10, 87, 155, 426],[23, 190, 38, 75, 56]]
        assert out_text == '你怎么样？'


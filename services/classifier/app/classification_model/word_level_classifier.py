import random
from torch import cuda, argmax, no_grad, load
from torch import random as torch_random
from transformers import BertTokenizer, PretrainedConfig
from stanfordcorenlp import StanfordCoreNLP
from .bert_classifier import BertClassifier
from collections import OrderedDict
import os

env = os.getenv("ENV")

if env != 'TEST':
    parser = StanfordCoreNLP(f"http://corenlp", port=9001,lang='zh')
else:
    parser = None

class WordLevelClassifier():
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        self.device = "cuda" if cuda.is_available() else "cpu"
        self.parser=parser
        random.seed(42)
        torch_random.manual_seed(42)
        cuda.manual_seed(42)
        model = BertClassifier()
        model.load_state_dict(load("./classification_model/state_dict_bert.pt",map_location= self.device))
        for parameter in model.parameters():
            parameter.requires_grad = False
        self.model = model
        self.model.to(self.device)
        self.model.eval()
    
    def encode(self, word):
        encoded_dict = self.tokenizer.encode_plus(
            text=word,  
            max_length=6,  
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
            )
        return {'input_ids':encoded_dict['input_ids'],
                              'attention_mask':encoded_dict['attention_mask']} 

    def preprocess(self,words):
        noPunctuation= [word for word in words if '\u4e00' <= word <= '\u9fff'] 
        return list(OrderedDict.fromkeys(noPunctuation))

    def classify(self, sentence):
        classifications=[]
        words = self.preprocess(parser.word_tokenize(sentence))
        for word in words:
            encodings =self.encode(word)
            with no_grad():
                output = self.model(encodings)
                level = argmax(output).item() 
            classifications.append({'word':word,'level':level+1})
        return classifications

            
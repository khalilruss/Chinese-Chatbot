from stanfordcorenlp import StanfordCoreNLP
import regex as re
from .grammarRules import grammarRules
import os
env = os.getenv("ENV")

if env != 'TEST':
    parser = StanfordCoreNLP(f"http://corenlp", port=9001,lang='zh')
else:
    parser = None

def parseSentence(sentence):
    tags = parser.pos_tag(sentence)
    pos_sent = ''.join([i for sub in tags for i in sub])
    return pos_sent

def extractGrammar(sentence):
    grammarExtracted=[]
    possibleMistakes=[]
    pos_sent= parseSentence(sentence)
    for grammar in grammarRules:
        if re.search(grammar['word'],sentence):
            if type(grammar['rules']) is str:
                p=re.compile(grammar['pattern'])
                matches=p.findall(pos_sent)
                if len(matches)==0:
                    possibleMistakes.append(grammar['word'])
                else:
                    grammarExtracted.append({'rule':grammar['rules'],'level':grammar['level']})
            else:
                numofMatches=0
                for pattern in grammar['rules']:
                    p=re.compile(pattern['pattern'])
                    matches=p.findall(pos_sent)
                    if len(matches)>0:
                        numofMatches+=1
                        grammarExtracted.append({'rule':pattern['rule'],'level':pattern['level']})
                if(numofMatches==0):
                    possibleMistakes.append(grammar['word'])
    return grammarExtracted, possibleMistakes

import sys, os
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from grammarRules import grammarRules
from grammar_rule_sentences import test_sentences
import regex as re
import pytest

@pytest.mark.skip(reason='Seperate Accurracy test for Grammar Extractor')
def test_accurracy():
    correct=0
    count=0
    for i, grammarRule in enumerate(grammarRules):
        if type(grammarRule['rules']) is str:
            sentences=test_sentences[i]
            p=re.compile(grammarRule['pattern'])
            for sentence in sentences:
                count+=1
                matches=p.findall(sentence)
                if len(matches)!=0:
                    correct+=1
        else:
            for j,pattern in enumerate(grammarRule['rules']):
                sentences=test_sentences[i][j]
                p=re.compile(pattern['pattern'])
                for sentence in sentences:
                    count+=1
                    matches=p.findall(sentence)
                    if len(matches)!=0:
                        correct+=1
        return round((correct/count)*100,2)

if __name__ == "__main__":
    print('Grammar Extractor Accuracy: ',test_accurracy())

from gensim.models import KeyedVectors
import numpy as np
from scipy.spatial.distance import cosine
import random

wv = KeyedVectors.load("../../../word_vectors/cc.zh.100.vec", mmap='r')
with open('./chatbot_utils/questions.txt') as my_file:
    questions = my_file.readlines()
questions=[question.strip() for question in questions]

def compare_to_history(history, possible_out_text, tokenizer):
    prev_texts=[]
    similarities=[]
    if history:
        if type(history[0])== int:
            prev_text, similarity = compare_sentences(possible_out_text, history, tokenizer)
            prev_texts.append(prev_text)
            similarities.append(similarity)
        else:
            for prev_text_ids in history:
                prev_text, similarity = compare_sentences(possible_out_text, prev_text_ids, tokenizer)
                prev_texts.append(prev_text)
                similarities.append(similarity)
        results={'possible_out_text':possible_out_text,'prev_texts': prev_texts, 'similarities':similarities}
        print(results)
        return results

def compare_sentences(possible_out_text, prev_text_ids, tokenizer):
    prev_text=tokenizer.decode(prev_text_ids, skip_special_tokens=True)
    prev_text_vector = np.mean([wv[word] for word in prev_text.split()],axis=0)
    possible_out_text_vector = np.mean([wv[word] for word in possible_out_text.split()],axis=0)
    similarity = 1 - cosine(prev_text_vector, possible_out_text_vector)
    return prev_text, similarity

def get_random_question(history, tokenizer):
    question=random.choice(questions)
    questions.remove(question)
    out_text= question
    question = " ".join(list(question.replace(" ", "")))
    history.append(tokenizer.convert_tokens_to_ids(tokenizer.tokenize(question)))
    return history, out_text
    
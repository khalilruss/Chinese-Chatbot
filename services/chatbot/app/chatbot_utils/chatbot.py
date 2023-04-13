import os
import logging
import random
from itertools import chain
from argparse import ArgumentParser
import regex as re

import torch
import torch.nn.functional as F

from transformers import OpenAIGPTLMHeadModel, BertTokenizer
from fastapi import WebSocket
from .sentence_simlarity import compare_to_history, get_random_question
MODEL_CHECKPOINT = './chatbot_utils/chatbot_model/'
SPECIAL_TOKENS = ["[CLS]", "[SEP]", "[PAD]", "[speaker1]", "[speaker2]"]
ARGS={ 'no_sample':False,'max_length': 30,'min_length':1,'temperature':0.7, 'top_k':0, 'top_p':0.9,'max_history':15}

class ChatBot():
    def __init__(self, websocket):
        model_class = OpenAIGPTLMHeadModel
        self.tokenizer = BertTokenizer.from_pretrained(MODEL_CHECKPOINT, do_lower_case=True)
        self.model = model_class.from_pretrained(MODEL_CHECKPOINT)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.websocket=websocket
        self.history= []
        self.model.to(self.device)
        self.model.eval()

    def top_filtering(self, logits, top_k=0, top_p=0.0, threshold=-float('Inf'), filter_value=-float('Inf')):
        """ Filter a distribution of logits using top-k, top-p (nucleus) and/or threshold filtering
            Args:
                logits: logits distribution shape (vocabulary size)
                top_k: <=0: no filtering, >0: keep only top k tokens with highest probability.
                top_p: <=0.0: no filtering, >0.0: keep only a subset S of candidates, where S is the smallest subset
                    whose total probability mass is greater than or equal to the threshold top_p.
                    In practice, we select the highest probability tokens whose cumulative probability mass exceeds
                    the threshold top_p.
                threshold: a minimal threshold to keep logits
        """
        assert logits.dim() == 1  # Only work for batch size 1 for now - could update but it would obfuscate a bit the code
        top_k = min(top_k, logits.size(-1))
        if top_k > 0:
            # Remove all tokens with a probability less than the last token in the top-k tokens
            indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
            logits[indices_to_remove] = filter_value

        if top_p > 0.0:
            # Compute cumulative probabilities of sorted tokens
            sorted_logits, sorted_indices = torch.sort(logits, descending=True)
            cumulative_probabilities = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

            # Remove tokens with cumulative probability above the threshold
            sorted_indices_to_remove = cumulative_probabilities > top_p
            # Shift the indices to the right to keep also the first token above the threshold
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = 0

            # Back to unsorted indices and set them to -infinity
            indices_to_remove = sorted_indices[sorted_indices_to_remove]
            logits[indices_to_remove] = filter_value

        indices_to_remove = logits < threshold
        logits[indices_to_remove] = filter_value

        return logits

    def build_input_from_segments(self, history, reply, with_eos=True):
        """ Build a sequence of input from 3 segments: persona, history and last reply """
        bos, eos, pad, speaker1, speaker2 = self.tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS)
        sequence = [[bos]] + history + [reply + ([eos] if with_eos else [])]
        sequence = [sequence[0]] + [[speaker2 if i % 2 else speaker1] + s for i, s in enumerate(sequence[1:])]
        instance = {}
        instance["input_ids"] = list(chain(*sequence))
        instance["token_type_ids"] = [bos] + [speaker2 if i % 2 else speaker1 for i, s in enumerate(sequence[1:])
                                            for _ in s]
        return instance, sequence

    def sample_sequence(self, history, current_output=None):
        special_tokens_ids = self.tokenizer.convert_tokens_to_ids(SPECIAL_TOKENS)
        if current_output is None:
            current_output = []

        for i in range(ARGS['max_length']):
            instance, sequence = self.build_input_from_segments(history, current_output, with_eos=False)
            input_ids = torch.tensor(instance["input_ids"], dtype=torch.long, device=self.device).unsqueeze(0)
            token_type_ids = torch.tensor(instance["token_type_ids"], dtype=torch.long, device=self.device).unsqueeze(0)

            logits, *_ = self.model(input_ids, token_type_ids=token_type_ids)
            logits = logits[0, -1, :] / ARGS['temperature']
            logits = self.top_filtering(logits, top_k=ARGS['top_k'], top_p=ARGS['top_p'])
            probs = F.softmax(logits, dim=-1)

            prev = torch.topk(probs, 1)[1] if ARGS['no_sample'] else torch.multinomial(probs, 1)
            if i < ARGS['min_length'] and prev.item() in special_tokens_ids:
                while prev.item() in special_tokens_ids:
                    prev = torch.multinomial(probs, num_samples=1)

            if prev.item() in special_tokens_ids:
                break
            current_output.append(prev.item())

        return current_output
   
    def tokenize(self, obj):
        if isinstance(obj, str):
            return self.tokenizer.convert_tokens_to_ids(self.tokenizer.tokenize(obj))
        if isinstance(obj, dict):
            return dict((n, tokenize(o)) for n, o in obj.items())
        return list(tokenize(o) for o in obj)
    
    def generate_out_ids(self):
        with torch.no_grad():
            out_ids = self.sample_sequence(self.history)
        return out_ids

    async def chat(self):
        await self.websocket.accept()
        while True:
            raw_text = await self.websocket.receive_text()
            if re.search('[a-zA-Z]',raw_text):
                out_text = 'Please send a message only using Chinese'
            else:
                print('raw_text before',raw_text)
                raw_text = " ".join(list(raw_text.replace(" ", "")))
                print('raw_text after',raw_text)
                self.history.append(self.tokenize(raw_text))

                index= 0 if len(self.history) == (2 * ARGS['max_history'] + 2) else 1
                while True:
                    out_ids = self.generate_out_ids()
                    if out_ids not in self.history[index::2]:
                        break
                possible_out_text=self.tokenizer.decode(out_ids, skip_special_tokens=True)
                if possible_out_text =='恩 恩 亲' or  possible_out_text =='恩 恩' or possible_out_text =='嗯 哼'or possible_out_text =='嗯 嗯 亲' or possible_out_text =='嗯 嗯' or possible_out_text =='哦 哦':
                    history, new_out_text=get_random_question(self.history,self.tokenizer)
                    self.history = history
                    out_text=new_out_text
                else:
                    if len(self.history)>1:
                        prev_comparison=compare_to_history(self.history[-2], possible_out_text, self.tokenizer)
                        if prev_comparison['similarities'][0] > 0.95:
                            history, new_out_text=get_random_question(self.history,self.tokenizer)
                            self.history = history
                            out_text=new_out_text
                        else:
                            history_comparisons=compare_to_history(self.history[index:-2:2], possible_out_text, self.tokenizer)
                            if history_comparisons and history_comparisons['similarities']:
                                if any(similarity > 0.95 for similarity in history_comparisons['similarities']):
                                    history, new_out_text=get_random_question(self.history,self.tokenizer)
                                    self.history = history
                                    out_text = new_out_text
                                else:
                                    self.history.append(out_ids)
                                    out_text =  possible_out_text.replace(" ", "")
                            else:
                                self.history.append(out_ids)
                                out_text =  possible_out_text.replace(" ", "")
                    else:
                        self.history.append(out_ids)
                        out_text = possible_out_text.replace(" ", "")
                self.history = self.history[-(2 * ARGS['max_history'] + 1):]
            await self.websocket.send_text(out_text)
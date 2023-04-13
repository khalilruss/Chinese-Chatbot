import torch
import json
import pandas as pd
from Bert import BertClassifier
from transformers import BertTokenizer
from train import move_to
from sklearn.metrics import accuracy_score, classification_report

def prepare_test_data(dfdataset,tokenizer):
    encoded_dicts =[]
    train_examples = [[text,label]
                    for i, (text, label) in enumerate(zip(dfdataset.iloc[:, 0], dfdataset.iloc[:, 1]))]
    for example in train_examples:
        encoded_dict = tokenizer.encode_plus(
            text=example[0],
            max_length=6,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
            )
        encoded_dicts.append({'input_ids':encoded_dict['input_ids'],
                              'attention_mask':encoded_dict['attention_mask']})
    return encoded_dicts

if __name__ == "__main__":

    model = BertClassifier(6)
    model.load_state_dict(torch.load("../services/classifier/app/classification_model/state_dict_bert.pt",map_location= "cuda"))
    model.to(torch.device("cuda"))

    with open('./hsk_test.txt', 'r') as filehandle:
        wordFreqList = json.load(filehandle)

    test_df= pd.DataFrame(wordFreqList)
    tokenizer=BertTokenizer.from_pretrained("bert-base-chinese")
    test_encodings = prepare_test_data(test_df, tokenizer)
    test_encodings=move_to(test_encodings,torch.device("cuda"))

    predictions=[]

    for test in test_encodings:
        move_to(test,torch.device("cuda"))
        with torch.no_grad():
            output=model(test)
            prediction=torch.argmax(output)
            predictions.append(prediction.item())
    
    predictions=[i+1 for i in predictions]
    accuracy = accuracy_score(test_df["labels"].tolist(), predictions)
    print('test accuracy: ', accuracy)
    print(classification_report(test_df["labels"].tolist(), predictions))

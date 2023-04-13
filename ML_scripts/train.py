import numpy as np
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from transformers import BertTokenizer, AdamW
import torch
import random
import time
from torch import argmax
from argparse import ArgumentParser
from Albert import AlbertClassifier
from Roberta import RobertaClassifier
from Bert import BertClassifier

def initialize_model(model_type,num_labels, train_df, batch_size=64,epochs=4):
    
    device = torch.device("cuda")

    if model_type == 'bert':
        model = BertClassifier(num_labels)
    elif model_type == 'albert':
        model = AlbertClassifier(num_labels)
    elif model_type == 'roberta':
        model = RobertaClassifier(num_labels)
    model.to(device)
    lr=1e-4
    steps_per_epoch= len(train_df)//batch_size +1
    
    param_optimizer = list(model.named_parameters())
    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [
            {
                "params": [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)],
                "weight_decay_rate": 0.01
                },
            {
                "params": [p for n, p in param_optimizer if any(nd in n for nd in no_decay)],
                "weight_decay_rate": 0.0
                },
            ]

    optimizer = AdamW(optimizer_grouped_parameters,
                      lr=lr,
                      eps=1e-8
                      )

    scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=lr, cycle_momentum=False, epochs=epochs, 
                                                  steps_per_epoch= steps_per_epoch)
    return model, optimizer, scheduler

def prepare_data(dfdataset,tokenizer):
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
        encoded_dicts.append({'input_ids':encoded_dict['input_ids'][0],
                              'attention_mask':encoded_dict['attention_mask'][0]})
    return encoded_dicts

class ChineseVocabDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        return self.encodings[idx], torch.tensor(self.labels[idx])

    def __len__(self):
        return len(self.labels)

def move_to(obj, device):
    if torch.is_tensor(obj):
        return obj.to(device)
    elif isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            res[k] = move_to(v, device)
        return res
    elif isinstance(obj, list):
        res = []
        for v in obj:
            res.append(move_to(v, device))
        return res
    else:
        raise TypeError("Invalid type for move_to")

def set_seed(seed_value=42):
    """Set seed for reproducibility.
    """
    random.seed(seed_value)
    np.random.seed(seed_value)
    torch.manual_seed(seed_value)
    torch.cuda.manual_seed_all(seed_value)

def train(model, train_dataloader, val_dataloader=None, epochs=4, evaluation=False):
    checkpoint={'model': model,
          'state_dict': model.state_dict(),
          'val_accuracy' : 0}
    """Train the BertClassifier model.
    """
    # Start training loop
    print("Start training...\n")
    device = torch.device("cuda")
    criterion=torch.nn.CrossEntropyLoss(ignore_index=-1)

    for epoch_i in range(epochs):
        # Print the header of the result table
        print(f"{'Epoch':^7} | {'Batch':^7} | {'Train Loss':^12} | {'Train Acc':^9} | {'Val Loss':^10} | {'Val Acc':^9} | {'Elapsed':^9}")
        print("-"*80)

        # Measure the elapsed time of each epoch
        t0_epoch, t0_batch = time.time(), time.time()

        # Reset tracking variables at the beginning of each epoch
        total_loss, batch_loss, batch_counts = 0, 0, 0
        train_accuracy = []

        # Put the model into the training mode
        model.train()

        # For each batch of training data...
        for step, batch in enumerate(train_dataloader):
            batch_counts +=1
            # Load batch to GPU
            inputs, labels = tuple(move_to(t,device) for t in batch)

            # Zero out any previously calculated gradients
            # optimizer.zero_grad()
            model.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            batch_loss += loss.item()
            total_loss += loss.item()
            
            # Get the predictions
            preds = torch.argmax(outputs, dim=1).flatten()

            # Calculate the accuracy rate
            accuracy = (preds == labels).cpu().numpy().mean() * 100
            train_accuracy.append(accuracy)

            # Perform a backward pass to calculate gradients
            loss.backward()

            # Clip the norm of the gradients to 1.0 to prevent "exploding gradients"
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

            # Update parameters and the learning rate
            optimizer.step()
            scheduler.step()

            # Print the loss values and time elapsed for every 20 batches
            if (step % 20 == 0 and step != 0) or (step == len(train_dataloader) - 1):
                # Calculate time elapsed for 20 batches
                time_elapsed = time.time() - t0_batch

                # Print training results
                print(f"{epoch_i + 1:^7} | {step:^7} | {batch_loss / batch_counts:^12.6f} | {accuracy:^9.2f} | {'-':^10} | {'-':^9} | {time_elapsed:^9.2f}")

                # Reset batch tracking variables
                batch_loss, batch_counts = 0, 0
                t0_batch = time.time()

        # Calculate the average loss over the entire training data
        avg_train_loss = total_loss / len(train_dataloader)
        avg_train_accuracy = np.mean(train_accuracy)
        print("-"*70)

        if evaluation == True:
            # After the completion of each training epoch, measure the model's performance
            # on our validation set.
            val_loss, val_accuracy = evaluate(model, val_dataloader)
            if checkpoint['val_accuracy']==0 or val_accuracy>checkpoint['val_accuracy']:
                checkpoint['state_dict'] = model.state_dict()
                checkpoint['val_accuracy'] = val_accuracy
            # Print performance over the entire training data
            time_elapsed = time.time() - t0_epoch
            
            print(f"{epoch_i + 1:^7} | {'-':^7} | {avg_train_loss:^12.6f} | {avg_train_accuracy:^9.2f} | {val_loss:^10.6f} | {val_accuracy:^9.2f} | {time_elapsed:^9.2f}")
            print("-"*80)
        print("\n")
    
    print("Training complete!")
    return checkpoint

def evaluate(model, val_dataloader):
    """After the completion of each training epoch, measure the model's performance
    on our validation set.
    """
    # Put the model into the evaluation mode. The dropout layers are disabled during
    # the test time.
    device = torch.device("cuda")
    model.eval()

    # Tracking variables
    val_accuracy = []
    val_loss = []
    criterion=torch.nn.CrossEntropyLoss(ignore_index=-1)

    # For each batch in our validation set...
    for batch in val_dataloader:
        # Load batch to GPU
        inputs, labels = tuple(move_to(t,device) for t in batch)

        # Compute logits
        with torch.no_grad():
            outputs = model(inputs)
            loss = criterion(outputs, labels)
        # Compute loss
        val_loss.append(loss.item())

        # Get the predictions
        preds = torch.argmax(outputs, dim=1).flatten()

        # Calculate the accuracy rate
        accuracy = (preds == labels).cpu().numpy().mean() * 100
        val_accuracy.append(accuracy)

    # Compute the average accuracy and loss over the validation set.
    val_loss = np.mean(val_loss)
    val_accuracy = np.mean(val_accuracy)

    return val_loss, val_accuracy

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--model', type=str, choices=['bert', 'albert', 'roberta'],help="pick model to train")
    parser.add_argument("--dataset", type=str, choices=['HSK','TOCFL', 'HSK_and_TOCFL'], help="pick dataset to train model with")
    parser.add_argument("--n_epochs", type=int, default=4, help="Number of training epochs")
    args = parser.parse_args()
    
    if args.dataset == 'HSK':
        filename='hsk_train.txt'
    elif args.dataset == 'TOCFL':
        filename='tocfl_train.txt'
    elif args.dataset == 'HSK_and_TOCFL':
        filename='tocfl_and_hsk_train.txt'

    with open(f'./{filename}', 'r') as filehandle:
        wordFreqList = json.load(filehandle)

    df= pd.DataFrame(wordFreqList)

    train_df, val_df = train_test_split(df, test_size= 0.1, stratify=df["labels"].tolist()) 
    
    if args.model == 'bert':
        model_name='bert-base-chinese'
    elif args.model == 'albert':
        model_name='clue/albert_chinese_tiny'
    elif args.model == 'roberta':
        model_name='clue/roberta_chinese_large'
    
    tokenizer=BertTokenizer.from_pretrained(model_name)
    train_encodings = prepare_data(train_df, tokenizer)
    val_encodings = prepare_data(val_df, tokenizer)

    y_train = [i-1 for i in train_df["labels"].tolist()]
    y_val = [i-1 for i in val_df["labels"].tolist()]

    train_dataset = ChineseVocabDataset(train_encodings, y_train)
    val_dataset = ChineseVocabDataset(val_encodings, y_val)

    labels_unique, counts= np.unique(y_train, return_counts=True)
    cw= 1/torch.tensor(counts, dtype=torch.float)
    class_weights = compute_class_weight('balanced', np.unique(y_train), y_train)
    example_weights=[cw[e] for e in y_train]


    train_dataloader = torch.utils.data.DataLoader(dataset=train_dataset, 
                                batch_size=64, 
                                sampler= torch.utils.data.WeightedRandomSampler(example_weights, len(example_weights)))
    val_dataloader = torch.utils.data.DataLoader(dataset=val_dataset, 
                                batch_size=64,
                                sampler= torch.utils.data.SequentialSampler(val_dataset)) 

    set_seed(42)    # Set seed for reproducibility
    model, optimizer, scheduler = initialize_model(args.model,len(labels_unique), train_df, batch_size=64,epochs=args.n_epochs)
    print(f'model:{args.model} dataset:{args.dataset} epochs:{args.n_epochs}')
    best_model=train(model, train_dataloader, val_dataloader, epochs=args.n_epochs, evaluation=True)
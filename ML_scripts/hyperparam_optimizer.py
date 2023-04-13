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
from Bert import BertClassifier

from train import move_to, prepare_data, ChineseVocabDataset, set_seed

from ray import tune
from ray.tune import CLIReporter
from ray.tune.schedulers import ASHAScheduler
from functools import partial
import os
from ray.tune.logger import DEFAULT_LOGGERS
from ray.tune.integration.wandb import WandbLogger

def train_and_optimize(config, train_dataset, val_dataset,example_weights, num_labels,checkpoint_dir="tf"):
    model = BertClassifier(num_labels)
    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda:0"
        if torch.cuda.device_count() > 1:
            model = torch.nn.DataParallel(model)
    model.to(device)
    
    train_dataloader = torch.utils.data.DataLoader(dataset=train_dataset, 
                                batch_size=config["batch_size"], 
                                sampler= torch.utils.data.WeightedRandomSampler(example_weights,
                                                                                len(example_weights)))
    val_dataloader = torch.utils.data.DataLoader(dataset=val_dataset, 
                                batch_size=config["batch_size"], 
                                sampler= torch.utils.data.SequentialSampler(val_dataset))
    
    criterion=torch.nn.CrossEntropyLoss(ignore_index=-1)
    steps_per_epoch= len(train_dataset)//config["batch_size"] +1
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
                      lr=config["lr"],
                      eps=1e-8
                  )
    scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=config["lr"], cycle_momentum=False, 
                                                    epochs=config["epochs"], steps_per_epoch= steps_per_epoch)
    
    for epoch_i in range(config["epochs"]):
        running_loss = 0.0
        epoch_steps = 0
        train_total = 0
        train_correct = 0
        for step, batch in enumerate(train_dataloader):
            # Load batch to GPU
            inputs, labels = tuple(move_to(t,device) for t in batch)

            # Zero out any previously calculated gradients
            model.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            preds = torch.argmax(outputs, dim=1).flatten()
            train_total += labels.size(0)
            train_correct += (preds == labels).sum().item()
            # Perform a backward pass to calculate gradients
            loss.backward()

            # Clip the norm of the gradients to 1.0 to prevent "exploding gradients"
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)

            # Update parameters and the learning rate
            optimizer.step()
            scheduler.step()

            running_loss += loss.item()
            epoch_steps += 1
            if step % 2000 == 1999:  # print every 2000 mini-batches
                print("[%d, %5d] loss: %.3f" % (epoch + 1, i + 1,
                                                running_loss / epoch_steps))
                running_loss = 0.0
                
        val_loss = 0.0
        val_steps = 0
        val_total = 0
        val_correct = 0
        for step, batch in enumerate(val_dataloader):
            inputs, labels = tuple(move_to(t,device) for t in batch)
            with torch.no_grad():
                outputs = model(inputs)
                preds = torch.argmax(outputs, dim=1).flatten()
                val_total += labels.size(0)
                val_correct += (preds == labels).sum().item()

                loss = criterion(outputs, labels)
                val_loss += loss.cpu().numpy()
                val_steps += 1

        with tune.checkpoint_dir(epoch_i) as checkpoint_dir:
            path = os.path.join(checkpoint_dir, "checkpoint")
            torch.save((model.state_dict(), optimizer.state_dict(),scheduler.state_dict()), path)
        val_loss=(val_loss / val_steps)
        val_accuracy=val_correct / val_total
        train_accuracy=train_correct / train_total

        tune.report(val_loss=val_loss, val_accuracy=val_accuracy, train_accuracy=train_accuracy)
    print("Finished Training")

if __name__ == "__main__":

    with open(f'hsk_train.txt', 'r') as filehandle:
        wordFreqList = json.load(filehandle)

    df= pd.DataFrame(wordFreqList)

    train_df, val_df = train_test_split(df, test_size= 0.1, stratify=df["labels"].tolist()) 
    
    model_name='bert-base-chinese'
    
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

    set_seed(42)
    num_samples=100
    max_num_epochs=10
    gpus_per_trial=1

    config = {
            "batch_size": 64,
            "lr": tune.uniform(1e-5, 1e-4),
            "epochs": 4,
            "wandb": {
                "project": "bert_optimize",
                "api_key":"6f7482633323f36f1c862b736055d52167c8c448",
                "log_config": True
            }
        }
    scheduler = ASHAScheduler(
        metric="val_accuracy",
        mode="max",
        max_t=max_num_epochs,
        grace_period=1,
        reduction_factor=2)

    reporter = CLIReporter(
        metric_columns=["val_loss", "val_accuracy", "train_accuracy","training_iteration"])

    result = tune.run(
        partial(train_and_optimize, train_dataset=train_dataset, 
                val_dataset=val_dataset, 
                example_weights=example_weights,
                num_labels=len(labels_unique)),
        resources_per_trial={"cpu": 1, "gpu": gpus_per_trial},
        config=config,
        num_samples=num_samples,
        scheduler=scheduler,
        progress_reporter=reporter,
        loggers=DEFAULT_LOGGERS + (WandbLogger, ),
        local_dir='./ray_results')

    best_trial = result.get_best_trial("val_accuracy", "max", "last")
    print("Best trial config: {}".format(best_trial.config))
    print("Best trial final validation loss: {}".format(
        best_trial.last_result["val_loss"]))
    print("Best trial final validation accuracy: {}".format(
        best_trial.last_result["val_accuracy"]))
from transformers import BertModel;
import torch;

class RobertaClassifier(torch.nn.Module):
    def __init__(self, num_labels,*args, **kwargs):
        super().__init__()
        self.num_labels = num_labels
        self.roberta= BertModel.from_pretrained('clue/roberta_chinese_large')
        self.pre_cls = torch.nn.Linear(self.roberta.config.hidden_size, self.roberta.config.hidden_size)
        self.cls = torch.nn.Linear(self.roberta.config.hidden_size, self.num_labels)
        
    def forward(self, inputs):
        outputs =self.roberta(inputs['input_ids'], attention_mask=inputs['attention_mask'])
        pooled_output = outputs[1]
        pooled_output = self.pre_cls(pooled_output)
        logits = self.cls(pooled_output)
        return logits
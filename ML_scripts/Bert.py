from transformers import BertModel;
import torch;

class BertClassifier(torch.nn.Module):
    def __init__(self, num_labels,*args, **kwargs):
        super().__init__()
        self.num_labels = num_labels
        self.bert= BertModel.from_pretrained('bert-base-chinese')
        self.pre_cls = torch.nn.Linear(self.bert.config.hidden_size, self.bert.config.hidden_size)
        self.cls = torch.nn.Linear(self.bert.config.hidden_size, self.num_labels)
        
    def forward(self, inputs):
        outputs =self.bert(inputs['input_ids'], attention_mask=inputs['attention_mask'])
        pooled_output = outputs[1]
        pooled_output = self.pre_cls(pooled_output)
        logits = self.cls(pooled_output)
        return logits
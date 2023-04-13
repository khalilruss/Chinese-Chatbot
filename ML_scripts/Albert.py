from transformers import AlbertModel;
import torch;

class AlbertClassifier(torch.nn.Module):
    def __init__(self, num_labels, *args, **kwargs):
        super().__init__()
        self.num_labels = num_labels
        self.albert= AlbertModel.from_pretrained("clue/albert_chinese_tiny")
        self.pre_cls = torch.nn.Linear(self.albert.config.hidden_size, self.albert.config.hidden_size)
        self.cls = torch.nn.Linear(self.albert.config.hidden_size, self.num_labels)
        
    def forward(self,inputs):
        outputs =self.albert(inputs['input_ids'], attention_mask=inputs['attention_mask'])
        pooled_output = outputs[1]
        pooled_output = self.pre_cls(pooled_output)
        logits = self.cls(pooled_output)
        return logits
import asyncio
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from transformers import RobertaTokenizer, RobertaModel
import torch.nn.functional as F

# Configuration
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "models/trained_model.pt"
MAX_LENGTH = 512

# Predefined label mapping
LABEL_MAP = {
    "block number dependency (BN)": 0,
    "dangerous delegatecall (DE)": 1,
    "ether frozen (EF)": 2,
    "ether strict equality (SE)": 3,
    "integer overflow (OF)": 4,
    "normal": 5,
    "reentrancy (RE)": 6,
    "timestamp dependency (TP)": 7,
    "unchecked external call (UC)": 8
}
IDX_TO_LABEL = {v: k for k, v in LABEL_MAP.items()}

class CodeClassifier(nn.Module):
    def __init__(self, num_labels):
        super().__init__()
        self.encoder = RobertaModel.from_pretrained("huggingface/CodeBERTa-small-v1")
        self.attn = nn.Linear(self.encoder.config.hidden_size, 1)
        self.classifier = nn.Linear(self.encoder.config.hidden_size, num_labels)

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        last_hidden_state = outputs.last_hidden_state
        attn_weights = torch.softmax(self.attn(last_hidden_state), dim=1)
        pooled_output = torch.sum(attn_weights * last_hidden_state, dim=1)
        logits = self.classifier(pooled_output)
        return logits, attn_weights

class AsyncModelLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    async def initialize(self):
        if not self._initialized:
            self.tokenizer = await asyncio.to_thread(
                RobertaTokenizer.from_pretrained, 
                "huggingface/CodeBERTa-small-v1"
            )
            model = CodeClassifier(num_labels=len(LABEL_MAP)).to(DEVICE)
            model.load_state_dict(
                await asyncio.to_thread(
                    torch.load, 
                    MODEL_PATH, 
                    map_location=DEVICE
                )
            )
            model.eval()
            self.model = model
            self._initialized = True
    
    @property
    def is_initialized(self):
        return self._initialized

async def load_model():
    """Async load model and tokenizer (singleton pattern)"""
    loader = AsyncModelLoader()
    await loader.initialize()
    return loader.model, loader.tokenizer

async def predict(model, tokenizer, code: str) -> str:
    """
    Async predict the vulnerability label for a single Solidity code snippet
    
    Args:
        model: Loaded model from load_model()
        tokenizer: Loaded tokenizer from load_model()
        code: Solidity code string to classify
        
    Returns:
        str: The predicted vulnerability label name
    """
    # Tokenize in a thread
    encoding = await asyncio.to_thread(
        tokenizer,
        code,
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
        return_tensors="pt"
    )
    
    input_ids = encoding["input_ids"].squeeze().unsqueeze(0).to(DEVICE)
    attention_mask = encoding["attention_mask"].squeeze().unsqueeze(0).to(DEVICE)
    
    # Run model inference in a thread
    logits, _ = await asyncio.to_thread(
        model,
        input_ids=input_ids,
        attention_mask=attention_mask
    )
    
    pred_idx = torch.argmax(logits, dim=1).item()
    return IDX_TO_LABEL[pred_idx]
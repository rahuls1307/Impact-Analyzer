import torch
from transformers import AutoTokenizer, AutoModel

class CodeEmbedder:
    def __init__(self, model_name="microsoft/graphcodebert-base"):
        self.device = (
            "cuda" if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available()
            else "cpu"
        )
        print(f"🔧 Using device: {self.device}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)

    def embed(self, text: str):
        if not text.strip():
            # Return zero vector for empty code blocks
            return torch.zeros(self.model.config.hidden_size).numpy()

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Mean-pool the token embeddings and flatten to 1D
        return outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

    def batch_embed(self, chunks):
        """
        Generate embeddings for a list of chunks (list of code strings).
        Returns list of 1D numpy arrays.
        """
        return [self.embed(chunk) for chunk in chunks]

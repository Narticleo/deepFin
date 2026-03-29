import torch
from torch import nn
import os
import torchvision
from torchvision.io import read_image, ImageReadMode
from torchvision.transforms import v2

# How to use this .py

# from recognizer import Recognizer

# if __name__ == '__main__':
    
#     recognizer = Recognizer('/your model path'):

#     embeddings = recognizer.get_embedding('/your id_pics path')

class _ResNet50(nn.Module):

    def __init__(self):
        super().__init__()
        self.model = torchvision.models.resnet50(weights='IMAGENET1K_V2')
        self.head = nn.Linear(self.model.fc.out_features, 2048, bias=False)

    def forward(self, x):
        y = self.model(x)
        y = self.head(y)
        return y

class Recognizer():

    def __init__(self, model_path: str):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        model = _ResNet50().to(self.device)
        model.load_state_dict(torch.load(model_path,map_location=torch.device(self.device)))
        self.model = model.to(self.device)
        self.model.eval()

        self.transform = v2.Compose([
            v2.Resize(size=(224, 224), antialias=True),
            v2.Normalize(mean=[0.5], std=[0.5])
        ])
    
    def get_embeddings(self, pic_paths: list) -> torch.tensor:
        data = []
        for pic_path in pic_paths:
            datum = read_image(pic_path, mode=ImageReadMode.RGB).to(self.device)
            datum = datum.float()
            datum = self.transform(datum)
            data.append(datum)
        data = torch.stack(data)
        
        with torch.no_grad():
            embeddings = self.model(data)

        return embeddings
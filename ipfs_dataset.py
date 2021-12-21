from torch.utils.data import Dataset
import io
import requests
import tarfile
from PIL import Image


class IPFSDataset(Dataset):
    """IPFS dataset."""

    def __init__(self, cid, transform=None, target_transform=None, url="http://127.0.0.1:5001/api/v0"):
        """
        Args: 
            cid (string): IPFS Directory CID with all the files.
            url (string): IPFS base URL
            transform (callable, optional): Optional transform to be applied
                on a sample.
            target_transform (callable, optional): A function/transform that takes
                in the target and transforms it.
        """
        response = requests.post(url+"/get?arg="+cid)
        contents = response.content
        tar = tarfile.open(fileobj=io.BytesIO(contents))
        self.isNotImage = lambda n: 'jpg' not in n and 'webp' not in n and 'png' not in n and 'gif' not in n and 'jpeg' not in n and "bmp" not in n and "tif" not in n and "ppm" not in n
        self.files = []
        self.classes = [name for name in tar.getnames(
        ) if self.isNotImage(name) and '/' in name]
        self.classes.sort()
        self.class_to_idx = {self.classes[i]
            : i for i in range(len(self.classes))}
        print(self.class_to_idx)
        for member in tar.getmembers():
            if member.isfile:
                extractedFile = tar.extractfile(member)
                if extractedFile is not None:
                    member.path
                    for classkey in self.class_to_idx:
                        if classkey in member.path:
                            img = Image.open(extractedFile)
                            self.files.append(
                                (img, self.class_to_idx[classkey]))
        tar.close()
        self.targets = [s[1] for s in self.files]
        self.cid = cid
        self.transform = transform
        self.target_transform = target_transform

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        image, target = self.files[idx]
        if self.transform is not None:
            image = self.transform(image)
        if self.target_transform is not None:
            target = self.target_transform(target)
        return image, target

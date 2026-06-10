import os
import random
from collections import Counter

import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

# =====================================================
# Transforms
# =====================================================

train_transforms = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

val_transforms = transforms.Compose([
    transforms.Resize((300, 300)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# =====================================================
# Dataset Class
# =====================================================

class FracAtlasDataset(Dataset):
    def __init__(
        self,
        image_dir,
        split="train",
        transform=None,
        train_ratio=0.70,
        val_ratio=0.15,
        seed=42
    ):
        self.image_dir = image_dir
        self.transform = transform
        self.split = split

        fractured_dir = os.path.join(image_dir, "Fractured")
        non_fractured_dir = os.path.join(image_dir, "Non_fractured")

        samples = []

        # Fractured -> label 1
        for img_name in os.listdir(fractured_dir):
            img_path = os.path.join(fractured_dir, img_name)

            if os.path.isfile(img_path):
                samples.append((img_path, 1))

        # Non-fractured -> label 0
        for img_name in os.listdir(non_fractured_dir):
            img_path = os.path.join(non_fractured_dir, img_name)

            if os.path.isfile(img_path):
                samples.append((img_path, 0))

        random.seed(seed)
        random.shuffle(samples)

        total = len(samples)

        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)

        if split == "train":
            self.samples = samples[:train_end]

        elif split == "val":
            self.samples = samples[train_end:val_end]

        elif split == "test":
            self.samples = samples[val_end:]

        else:
            raise ValueError(
                "split must be one of ['train', 'val', 'test']"
            )

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]

        image = Image.open(img_path).convert("RGB")

        if self.transform:
            image = self.transform(image)

        return image, label


# =====================================================
# Dataloaders
# =====================================================

def get_dataloaders(data_dir, batch_size=32):

    train_dataset = FracAtlasDataset(
        image_dir=data_dir,
        split="train",
        transform=train_transforms
    )

    val_dataset = FracAtlasDataset(
        image_dir=data_dir,
        split="val",
        transform=val_transforms
    )

    test_dataset = FracAtlasDataset(
        image_dir=data_dir,
        split="test",
        transform=val_transforms
    )

    # ---------------------------------------------
    # WeightedRandomSampler for class imbalance
    # ---------------------------------------------

    train_labels = [label for _, label in train_dataset.samples]

    class_counts = Counter(train_labels)

    class_weights = {
        cls: 1.0 / count
        for cls, count in class_counts.items()
    }

    sample_weights = [
        class_weights[label]
        for label in train_labels
    ]

    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=0
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0
    )

    return train_loader, val_loader, test_loader


# =====================================================
# Quick Test
# =====================================================

if __name__ == "__main__":

    data_dir = "../data/raw/FracAtlas/images"

    train_loader, val_loader, test_loader = get_dataloaders(
        data_dir,
        batch_size=16
    )

    print(f"Train batches: {len(train_loader)}")
    print(f"Val batches: {len(val_loader)}")
    print(f"Test batches: {len(test_loader)}")

    images, labels = next(iter(train_loader))

    print("Image batch shape:", images.shape)
    print("Label batch shape:", labels.shape)
import os
import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import ReduceLROnPlateau

from dataset import get_dataloaders
from model import get_model, unfreeze_model


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:

        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(outputs, labels)

        loss.backward()

        optimizer.step()

        running_loss += loss.item() * images.size(0)

        _, predicted = torch.max(outputs, 1)

        correct += (predicted == labels).sum().item()

        total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    return epoch_loss, epoch_acc


def evaluate(model, loader, criterion, device):
    model.eval()

    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)

            _, predicted = torch.max(outputs, 1)

            correct += (predicted == labels).sum().item()

            total += labels.size(0)

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    return epoch_loss, epoch_acc


def train(config):

    device = config["device"]

    train_loader, val_loader, test_loader = get_dataloaders(
        data_dir=config["data_dir"],
        batch_size=config["batch_size"]
    )

    model = get_model(
        num_classes=2,
        device=device
    )

    # -----------------------------------
    # Class weights
    # -----------------------------------

    class_counts = [3366, 717]

    class_weights = torch.tensor(
        [
            1 / class_counts[0],
            1 / class_counts[1]
        ],
        dtype=torch.float32
    )

    class_weights = (
        class_weights / class_weights.sum()
    ).to(device)

    criterion = nn.CrossEntropyLoss(
        weight=class_weights
    )

    optimizer = Adam(
        filter(
            lambda p: p.requires_grad,
            model.parameters()
        ),
        lr=config["learning_rate"]
    )

    scheduler = ReduceLROnPlateau(
        optimizer,
        mode="min",
        patience=3,
        factor=0.1
    )

    best_val_acc = 0.0

    save_dir = os.path.dirname(
        config["save_path"]
    )

    os.makedirs(
        save_dir,
        exist_ok=True
    )

    for epoch in range(config["num_epochs"]):
        
        print(f"\nEpoch [{epoch+1}/{config['num_epochs']}] training...")

        # -----------------------------------
        # Fine-tuning phase
        # -----------------------------------

        if epoch == config["unfreeze_epoch"]:

            print(
                "\nUnfreezing last layers..."
            )

            unfreeze_model(
                model,
                num_layers=40
            )

            optimizer = Adam(
                filter(
                    lambda p: p.requires_grad,
                    model.parameters()
                ),
                lr=1e-4
            )

        train_loss, train_acc = train_one_epoch(
            model,
            train_loader,
            optimizer,
            criterion,
            device
        )

        val_loss, val_acc = evaluate(
            model,
            val_loader,
            criterion,
            device
        )

        scheduler.step(val_loss)

        print(
            f"Epoch [{epoch+1}/{config['num_epochs']}] | "
            f"Train Loss: {train_loss:.4f} | "
            f"Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} | "
            f"Val Acc: {val_acc:.4f}"
        )

        if val_acc > best_val_acc:

            best_val_acc = val_acc

            torch.save(
                model.state_dict(),
                config["save_path"]
            )

            print(
                f"Best model saved "
                f"(Val Acc = {val_acc:.4f})"
            )

    print(
        f"\nTraining Complete. "
        f"Best Val Acc = {best_val_acc:.4f}"
    )

    return model


if __name__ == "__main__":

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    config = {
        "data_dir": "../data/raw/FracAtlas/images",
        "batch_size": 32,
        "num_epochs": 30,
        "learning_rate": 1e-3,
        "device": device,
        "save_path": "../models/best_model.pth",
        "unfreeze_epoch": 5
    }

    train(config)
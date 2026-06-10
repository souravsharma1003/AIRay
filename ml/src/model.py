import torch
import torch.nn as nn
from efficientnet_pytorch import EfficientNet


class FractureDetector(nn.Module):
    def __init__(self, num_classes=2, pretrained=True):
        super().__init__()

        if pretrained:
            self.base_model = EfficientNet.from_pretrained(
                "efficientnet-b3"
            )
        else:
            self.base_model = EfficientNet.from_name(
                "efficientnet-b3"
            )

        # Freeze all parameters
        for param in self.base_model.parameters():
            param.requires_grad = False

        # Replace classification head
        self.base_model._fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(1536, num_classes)
        )

        # Train new classifier
        for param in self.base_model._fc.parameters():
            param.requires_grad = True

    def forward(self, x):
        return self.base_model(x)


def get_model(num_classes=2, device="cpu"):
    model = FractureDetector(
        num_classes=num_classes,
        pretrained=True
    )

    model = model.to(device)

    total_params = sum(
        p.numel()
        for p in model.parameters()
    )

    trainable_params = sum(
        p.numel()
        for p in model.parameters()
        if p.requires_grad
    )

    print(f"Total Parameters: {total_params:,}")
    print(f"Trainable Parameters: {trainable_params:,}")

    return model


def unfreeze_model(model, num_layers=20):
    """
    Unfreeze the last `num_layers`
    parameter tensors of EfficientNet.
    """

    params = list(model.base_model.parameters())

    for param in params[-num_layers:]:
        param.requires_grad = True

    trainable_params = sum(
        p.numel()
        for p in model.parameters()
        if p.requires_grad
    )

    print(
        f"Trainable Parameters After Unfreezing: "
        f"{trainable_params:,}"
    )

    return model


if __name__ == "__main__":

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    model = get_model(
        num_classes=2,
        device=device
    )

    dummy_input = torch.randn(
        4,
        3,
        300,
        300
    ).to(device)

    output = model(dummy_input)

    print("Output Shape:", output.shape)

    model = unfreeze_model(
        model,
        num_layers=20
    )
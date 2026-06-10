import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt

from PIL import Image

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from dataset import get_dataloaders, val_transforms
from model import get_model


def evaluate_model(model, test_loader, device):
    """
    Evaluate model on test set.
    Prints:
    - Accuracy
    - Precision
    - Recall
    - F1-score
    - Confusion Matrix
    """

    model.eval()

    all_preds = []
    all_labels = []

    with torch.no_grad():

        for images, labels in test_loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            preds = torch.argmax(outputs, dim=1)

            all_preds.extend(
                preds.cpu().numpy()
            )

            all_labels.extend(
                labels.cpu().numpy()
            )

    accuracy = accuracy_score(
        all_labels,
        all_preds
    )

    print("\n" + "=" * 50)
    print("TEST SET RESULTS")
    print("=" * 50)

    print(f"\nAccuracy: {accuracy:.4f}")

    print("\nClassification Report:\n")

    print(
        classification_report(
            all_labels,
            all_preds,
            target_names=[
                "Non_Fractured",
                "Fractured"
            ]
        )
    )

    cm = confusion_matrix(
        all_labels,
        all_preds
    )

    print("\nConfusion Matrix:\n")
    print(cm)

    return accuracy, cm


def generate_gradcam(
    model,
    image_tensor,
    target_layer,
    device
):
    """
    Generate Grad-CAM heatmap for a single image.
    """

    activations = []
    gradients = []

    def forward_hook(
        module,
        input,
        output
    ):
        activations.append(output)

    def backward_hook(
        module,
        grad_input,
        grad_output
    ):
        gradients.append(
            grad_output[0]
        )

    forward_handle = (
        target_layer.register_forward_hook(
            forward_hook
        )
    )

    backward_handle = (
        target_layer.register_full_backward_hook(
            backward_hook
        )
    )

    model.eval()

    image_tensor = (
        image_tensor
        .unsqueeze(0)
        .to(device)
        .requires_grad_(True)
    )

    with torch.enable_grad():
        outputs = model(image_tensor)

    predicted_class = outputs.argmax(dim=1).item()

    model.zero_grad()

    with torch.enable_grad():
        outputs[0, predicted_class].backward(retain_graph=True)

    predicted_class = (
        outputs.argmax(dim=1).item()
    )

    model.zero_grad()

    outputs[
        0,
        predicted_class
    ].backward()

    feature_maps = (
        activations[0]
        .detach()
    )

    grads = (
        gradients[0]
        .detach()
    )

    pooled_grads = torch.mean(
        grads,
        dim=(2, 3),
        keepdim=True
    )

    weighted_maps = (
        pooled_grads *
        feature_maps
    )

    heatmap = torch.mean(
        weighted_maps,
        dim=1
    ).squeeze()

    heatmap = F.relu(
        heatmap
    )

    heatmap = (
        heatmap /
        (heatmap.max() + 1e-8)
    )

    heatmap = (
        heatmap
        .unsqueeze(0)
        .unsqueeze(0)
    )

    heatmap = F.interpolate(
        heatmap,
        size=(300, 300),
        mode="bilinear",
        align_corners=False
    )

    heatmap = (
        heatmap
        .squeeze()
        .cpu()
        .numpy()
    )

    forward_handle.remove()
    backward_handle.remove()

    return heatmap


def visualize_gradcam(
    image_path,
    model,
    device,
    save_path="../outputs/gradcam_result.jpg"
):
    """
    Visualize Grad-CAM heatmap and overlay.
    """

    os.makedirs(
        os.path.dirname(save_path),
        exist_ok=True
    )

    pil_image = (
        Image.open(image_path)
        .convert("RGB")
    )

    image_tensor = val_transforms(
        pil_image
    )

    target_layer = (
        model.base_model._conv_head
    )

    heatmap = generate_gradcam(
        model,
        image_tensor,
        target_layer,
        device
    )

    original = np.array(
        pil_image.resize(
            (300, 300)
        )
    )

    heatmap_uint8 = np.uint8(
        heatmap * 255
    )

    colored_heatmap = cv2.applyColorMap(
        heatmap_uint8,
        cv2.COLORMAP_JET
    )

    colored_heatmap = cv2.cvtColor(
        colored_heatmap,
        cv2.COLOR_BGR2RGB
    )

    overlay = cv2.addWeighted(
        original,
        0.6,
        colored_heatmap,
        0.4,
        0
    )

    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.imshow(original)
    plt.title("Original Image")
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.imshow(colored_heatmap)
    plt.title("Grad-CAM Heatmap")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.imshow(overlay)
    plt.title("Overlay")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

    cv2.imwrite(
        save_path,
        cv2.cvtColor(
            overlay,
            cv2.COLOR_RGB2BGR
        )
    )

    print(
        f"\nGrad-CAM saved to: {save_path}"
    )


if __name__ == "__main__":

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(f"Using device: {device}")

    model = get_model(
        num_classes=2,
        device=device
    )

    model.load_state_dict(
        torch.load(
            "../models/best_model.pth",
            map_location=device
        )
    )

    print("\nModel loaded successfully.")

    _, _, test_loader = get_dataloaders(
        "../data/raw/FracAtlas/images",
        batch_size=32
    )

    evaluate_model(
        model,
        test_loader,
        device
    )

    
    visualize_gradcam(
        image_path="../data/raw/FracAtlas/images/Fractured/IMG0000777.jpg",
        model=model,
        device=device
    )
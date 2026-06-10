import os
import sys
import io
import cv2
import base64
import numpy as np
import torch

from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../src"
        )
    )
)

from model import FractureDetector
from dataset import val_transforms
from evaluate import generate_gradcam

router = APIRouter()

MODEL = None
DEVICE = None

MODEL_VERSION = "1.0.0"

def load_model():
    global MODEL
    global DEVICE

    if MODEL is not None:
        return MODEL, DEVICE

    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    model = FractureDetector(
        num_classes=2,
        pretrained=False
    )

    weights_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../../models/best_model.pth"
        )
    )

    model.load_state_dict(
        torch.load(
            weights_path,
            map_location=DEVICE
        )
    )

    model.to(DEVICE)
    model.eval()

    MODEL = model

    return MODEL, DEVICE

@router.post("/")
async def predict_image(
    file: UploadFile = File(...)
):
    try:
        model, device = load_model()

        image_bytes = await file.read()

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        image_tensor = val_transforms(image)

        with torch.no_grad():
            outputs = model(image_tensor.unsqueeze(0).to(device))
            probabilities = torch.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0, predicted_class].item()

        class_names = {
            0: "Non_Fractured",
            1: "Fractured"
        }

        target_layer = model.base_model._conv_head

        heatmap = generate_gradcam(
            model,
            image_tensor,
            target_layer,
            device
        )

        original = np.array(image.resize((300, 300)))
        heatmap_uint8 = np.uint8(heatmap * 255)

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
        overlay_bgr = cv2.cvtColor(
            overlay,
            cv2.COLOR_RGB2BGR
        )

        success, buffer = cv2.imencode(".jpg", overlay_bgr)
        if not success:
            raise Exception("Failed to encode image")

        gradcam_base64 = base64.b64encode(buffer.tobytes()).decode("utf-8")

        return {
            "prediction": class_names[predicted_class],
            "confidence": round(confidence, 4),
            "gradcam_image": gradcam_base64,
            "model_version": MODEL_VERSION
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

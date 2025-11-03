from fastapi import APIRouter, UploadFile, File
from typing import List
from utils.model_prediction_utils import predict_bulk_images
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/predict")
async def bulk_predict(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        contents = await file.read()
        filename = file.filename

        try:
            prediction = predict_bulk_images(contents, filename)
            results.append({
                "filename": filename,
                "prediction": prediction["label"],
                "confidence": prediction["confidence"]
            })
        except Exception as e:
            results.append({
                "filename": filename,
                "error": str(e)
            })
    return JSONResponse(content={"results": results})

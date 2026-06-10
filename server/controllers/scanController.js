const scanModel = require("../models/Scan");
const { errorResponse, successResponse } = require("../utils/apiResponse");
const FormData = require("form-data");
const axios = require("axios");

module.exports.uploadScan = async (req, res, next) => {
    try {
        const user = req.user._id;
        const bodyPart = req.body.bodyPart || "unknown";
        const file = req.file;
        if (!file) {
            return errorResponse(res, "No image uploaded", 400);
        }
        const form = new FormData();
        form.append("file", req.file.buffer, req.file.originalname);

        const response = await axios.post("http://localhost:8000/predict/", form, {
            headers: form.getHeaders()
        })

        const data = response.data;

        const scan = await scanModel.create({
            userId: user,
            originalImage: file.originalname,
            gradcamImage: data.gradcam_image,
            prediction: data.prediction,
            confidence: data.confidence,
            modelVersion: data.model_version,
            bodyPart: bodyPart
        })

        return successResponse(res, "Scan created successfully", scan, 201);

    } catch (error) {
        next(error)
    }
}

module.exports.getUserScans = async (req, res,next) => {
    try {
        const userId = req.user._id;

        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 10;
        const skip = (page - 1) * limit;

        const scans = await scanModel
            .find({ userId })
            .sort({ createdAt: -1 })
            .skip(skip)
            .limit(limit);

        const total = await scanModel.countDocuments({ userId });

        return successResponse(
            res,
            "Scans fetched successfully",
            {
                scans,
                currentPage: page,
                totalPages: Math.ceil(total / limit),
                totalScans: total,
            },
            200
        );
    } catch (error) {
        return next(error);
    }
};

module.exports.getScanById=async(req,res,next)=>{
    try {
        const scanId=req.params.id;
        const scan=await scanModel.findById(scanId);
        if(!scan){
            return errorResponse(res,"Scan not found",404);
        }
        const isOwner=scan.userId.equals(req.user._id);
        if(!isOwner){
            return errorResponse(res,"Not authorized",403);
        }
        return successResponse(res,"Scan fetched successfully",scan,200);
    } catch (error) {
        return next(error);
    }
}

module.exports.deleteScan=async(req,res,next)=>{
    try {
        const scanId=req.params.id;
        const scan=await scanModel.findById(scanId);
        if(!scan){
            return errorResponse(res,"Scan not found",404);
        }
        const isOwner=scan.userId.equals(req.user._id);
        if(!isOwner){
            return errorResponse(res,"Not authorized",403);
        }
        await scanModel.deleteOne({_id:scanId});
        return successResponse(res,"Scan deleted successfully",null,200);
    } catch (error) {
        return next(error);
    }
}
const userModel = require("../models/User");
const scanModel = require("../models/Scan");
const {successResponse,errorResponse} = require("../utils/apiResponse");

module.exports.getAllUsers = async (req, res,next) => {
    try {
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 10;
        const skip = (page - 1) * limit;

        const users = await userModel
            .find()
            .select("-password")
            .skip(skip)
            .limit(limit);

        const totalUsers = await userModel.countDocuments();

        return successResponse(
            res,
            "Users fetched successfully",
            {
                users,
                pagination: {
                    currentPage: page,
                    totalPages: Math.ceil(totalUsers / limit),
                    totalUsers,
                    limit,
                },
            },
            200
        );
    } catch (error) {
        return next(error);
    }
};

module.exports.getAllScans = async (req, res, next) => {
    try {
        const page = parseInt(req.query.page) || 1;
        const limit = parseInt(req.query.limit) || 10;
        const skip = (page - 1) * limit;

        const scans = await scanModel
            .find()
            .populate("userId", "name email")
            .sort({ createdAt: -1 })
            .skip(skip)
            .limit(limit);

        const totalScans = await scanModel.countDocuments();

        return successResponse(
            res,
            "Scans fetched successfully",
            {
                scans,
                pagination: {
                    currentPage: page,
                    totalPages: Math.ceil(totalScans / limit),
                    totalScans,
                    limit,
                },
            },
            200
        );
    } catch (error) {
        return next(error);
    }
};
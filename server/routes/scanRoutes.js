const {Router}=require("express");
const upload=require("../middleware/upload");
const {protect}=require("../middleware/authMiddleware");
const {uploadScan,getUserScans,getScanById,deleteScan}=require("../controllers/scanController");

const scanRouter=Router();

scanRouter.post("/",protect,upload,uploadScan);

scanRouter.get("/",protect,getUserScans);

scanRouter.get("/:id",protect,getScanById);

scanRouter.delete("/:id",protect,deleteScan);

module.exports = scanRouter;
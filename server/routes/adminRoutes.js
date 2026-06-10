const { Router } = require("express");

const adminController = require("../controllers/adminController");
const {protect,adminOnly} = require("../middleware/authMiddleware");

const adminRouter = Router();

adminRouter.get("/users",protect,adminOnly,adminController.getAllUsers);

adminRouter.get("/scans",protect,adminOnly,adminController.getAllScans);

module.exports = adminRouter;
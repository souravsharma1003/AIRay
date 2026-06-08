require("dotenv").config();
const express = require("express");
const helmet = require("helmet");
const cors = require("cors");
const morgan = require("morgan");

const connectDb = require("./config/db");

const app = express();

app.use(helmet());
app.use(cors());

if (process.env.NODE_ENV === "development") {
    app.use(morgan("dev"))
}

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get("/api/health", (req, res) => {
    return res.status(200).json({
        status: "ok",
        message: "Server is running"
    })
})

const startServer = async () => {
    await connectDb();
    const PORT = process.env.PORT || 5000

    app.listen(PORT, () => {
        console.log("Server connected successfully on PORT:", PORT);
    })
}

startServer();
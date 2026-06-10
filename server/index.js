require('dotenv').config()
const express = require('express')
const helmet = require('helmet')
const cors = require('cors')
const morgan = require('morgan')
const cookieParser = require('cookie-parser')

const connectDb = require('./config/db')
const handleError = require('./middleware/errorHandler')
const { generalLimiter } = require('./middleware/rateLimiter')
const authRouter = require('./routes/authRoutes');
const scanRouter=require("./routes/scanRoutes");
const adminRouter=require("./routes/adminRoutes");

const app = express()

app.use(helmet())
app.use(cors())

if (process.env.NODE_ENV === 'development') {
  app.use(morgan('dev'))
}

app.use(express.json())
app.use(express.urlencoded({ extended: true }))

app.use(cookieParser())

app.use('/api', generalLimiter)

app.get('/api/health', (req, res) => {
  return res.status(200).json({
    status: 'ok',
    message: 'Server is running',
  })
})

app.use('/api/auth', authRouter);
app.use("/api/scans",scanRouter);
app.use("/api/admin",adminRouter);

app.use(handleError)

const startServer = async () => {
  await connectDb()
  const PORT = process.env.PORT || 5000

  app.listen(PORT, () => {
    console.log('Server connected successfully on PORT:', PORT)
  })
}

startServer()

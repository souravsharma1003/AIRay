const { Router } = require('express')
const authController = require('../controllers/authController')
const validate = require('../middleware/validate')
const { registerSchema, loginSchema } = require('../validators/authValidator')
const { protect } = require('../middleware/authMiddleware')

const authRouter = Router()

authRouter.post('/register', validate(registerSchema), authController.register)

authRouter.post('/login', validate(loginSchema), authController.login)

authRouter.post('/logout', protect, authController.logout)

authRouter.post('/refresh-token', authController.refreshAccessToken)

module.exports = authRouter

const { errorResponse } = require('../utils/apiResponse')
const jwt = require('jsonwebtoken')
const userModel = require('../models/User')

module.exports.protect = async (req, res, next) => {
  try {
    if (
      !req.headers.authorization ||
      !req.headers.authorization.startsWith('Bearer ')
    ) {
      return errorResponse(res, 'Not authorized, no token', 401)
    }
    const token = req.headers.authorization.split(' ')[1]
    if (!token) {
      return errorResponse(res, 'Not authorized, no token', 401)
    }
    const decoded = jwt.verify(token, process.env.ACCESS_TOKEN_SECRET)
    const user = await userModel.findById(decoded.id)
    if (!user) {
      return errorResponse(res, 'Not authorized, user not found', 401)
    }

    req.user = user

    return next()
  } catch (error) {
    return next(error)
  }
}

module.exports.adminOnly = (req, res, next) => {
  try {
    const isAdmin = req.user.role === 'admin'
    if (!isAdmin) {
      return errorResponse(res, 'Access denied, admin only', 403)
    }
    return next()
  } catch (error) {
    return next(error)
  }
}

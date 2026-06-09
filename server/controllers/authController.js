const userModel = require('../models/User')
const { errorResponse, successResponse } = require('../utils/apiResponse')
const {
  generateAccessToken,
  generateRefreshToken,
} = require('../utils/generateTokens')
const jwt = require('jsonwebtoken')

module.exports.register = async (req, res, next) => {
  try {
    const { name, email, password } = req.body
    const userExists = await userModel.findOne({ email })
    if (userExists) {
      return errorResponse(res, 'Email already in use', 409)
    }
    const newUser = await userModel.create({
      name,
      email,
      password,
    })
    const refreshToken = generateRefreshToken(newUser._id)
    const accessToken = generateAccessToken(newUser._id, 'user')

    newUser.refreshToken = refreshToken
    await newUser.save()

    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: true,
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000,
    })
    const userToReturn = await userModel.findById(newUser._id)
    return successResponse(
      res,
      'User registered successfully',
      {
        accessToken,
        user: userToReturn,
      },
      201
    )
  } catch (error) {
    return next(error)
  }
}

module.exports.login = async (req, res, next) => {
  try {
    const { email, password } = req.body

    const user = await userModel.findOne({ email }).select('+password')

    if (!user) {
      return errorResponse(res, 'Invalid credentials', 401)
    }

    const isPasswordMatch = await user.comparePassword(password)

    if (!isPasswordMatch) {
      return errorResponse(res, 'Invalid credentials', 401)
    }

    const refreshToken = generateRefreshToken(user._id)
    const accessToken = generateAccessToken(user._id, 'user')

    user.refreshToken = refreshToken
    await user.save()

    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: true,
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000,
    })
    const userToReturn = await userModel.findById(user._id)
    return successResponse(
      res,
      'User logged-in successfully',
      {
        accessToken,
        user: userToReturn,
      },
      200
    )
  } catch (error) {
    return next(error)
  }
}

module.exports.logout = async (req, res, next) => {
  try {
    const userId = req.user._id
    const user = await userModel.findById(userId)
    user.refreshToken = null
    await user.save()
    res.clearCookie('refreshToken')
    return successResponse(res, 'Logged out successfully', null, 200)
  } catch (error) {
    return next(error)
  }
}

module.exports.refreshAccessToken = async (req, res, next) => {
  try {
    const refreshToken = req.cookies.refreshToken
    if (!refreshToken) {
      return errorResponse(res, 'No refresh token', 401)
    }
    const decoded = jwt.verify(refreshToken, process.env.REFRESH_TOKEN_SECRET)
    const user = await userModel.findById(decoded.id)
    const accessToken = generateAccessToken(user._id, 'user')
    return successResponse(
      res,
      'New Access Token generated',
      {
        accessToken,
        user,
      },
      200
    )
  } catch (error) {
    return next(error)
  }
}

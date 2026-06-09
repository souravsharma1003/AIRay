const jwt = require('jsonwebtoken')

module.exports.generateAccessToken = (userId, role) => {
  const token = jwt.sign(
    {
      id: userId,
      role,
    },
    process.env.ACCESS_TOKEN_SECRET,
    { expiresIn: '15m' }
  )

  return token
}

module.exports.generateRefreshToken = (userId) => {
  const token = jwt.sign(
    {
      id: userId,
    },
    process.env.REFRESH_TOKEN_SECRET,
    { expiresIn: '7d' }
  )
  return token
}

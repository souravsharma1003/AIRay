const Joi = require('joi')

const registerSchema = Joi.object({
  name: Joi.string().required().min(2).max(50),
  email: Joi.string().required().email(),
  password: Joi.string().required().min(6).max(32),
})

const loginSchema = Joi.object({
  email: Joi.string().required().email(),
  password: Joi.string().required().min(6),
})

module.exports = { registerSchema, loginSchema }

module.exports = (schema) => (req, res, next) => {
  const { error } = schema.validate(req.body)
  if (error) {
    return next({
      message: error.message,
      statusCode: 400,
    })
  }
  return next()
}

const {rateLimit}=require("express-rate-limit");

module.exports.generalLimiter=rateLimit({
    windowMs:15*60*1000,
    limit:100,
    message:"Too many requests, please try again later"
})

module.exports.authLimiter=rateLimit({
    windowMs:15*60*1000,
    limit:10,
    message:"Too many authentication attempts, please try again later"
})
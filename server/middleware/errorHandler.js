const handleError=(err,req,res,next)=>{
        return res.status(err.statusCode || 500).json({
            success:false,
            message:err.message || "Internal Server Error",
            stack:process.env.NODE_ENV==="development"?err.stack:null
        })
}

module.exports = handleError
const mongoose=require("mongoose");

const scanSchema=new mongoose.Schema({
    userId:{
        type:mongoose.Schema.Types.ObjectId,
        ref:"User",
        required:true,
        index:true
    },
    originalImage:{
        type:String,
        required:true
    },
    gradcamImage:{
        type:String,
        required:true
    },
    prediction:{
        type:String,
        enum:["Fractured","Non_Fractured"],
        required:true
    },
    confidence:{
        type:Number,
        required:true,
        min:0,
        max:1
    },
    modelVersion:{
        type:String,
        default:"1.0.0"
    },
    bodyPart:{
        type:String,
        enum:["hand","leg","hip","shoulder","unknown"],
        default:"unknown"
    },
    notes:{
        type:String,
        default:null
    }
},{timestamps:true})

module.exports=mongoose.model("Scan",scanSchema);
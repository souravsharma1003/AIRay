const mongoose=require("mongoose");

const connectDb=async()=>{
    const url=process.env.MONGO_URI;
    try {
        const conn=await mongoose.connect(url);
        console.log(`Database connected: ${conn.connection.host}`);
    } catch (error) {
        console.error("Error connecting to the database: ",error.message);
        process.exit(1);
    }
}

module.exports=connectDb;
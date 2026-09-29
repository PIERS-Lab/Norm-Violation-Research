// require is the javascript way of including libraries
const { current } = require("@reduxjs/toolkit");
const express = require("express");
// use the multer library, then set up the upload middleware for use
const multer = require("multer");
const upload = multer({dest: "uploads/"});
// using cors tells the server to allow code from other origins to send and received dats
const cors = require("cors");
// create the server itself using express
const app = express();
// Tells the server to chack and parse json files whenever a request come in
let currentState = {hscore: 0, lrscore:0, rrscore:0, msg: "raw"};
app.use(cors({
  origin: 'http://localhost:5173'
}));
app.use(express.json());
// tells the server what to do when recieving data, empty means it'll only run on startup.
app.listen(3000, () => {console.log("server running!");});
app.use((req, res, next) => {
    console.log("incoming request", req.method, req.url);
    next();
});

app.get("/", (req, res) =>{
    res.send("Hello!")
});

app.get("/state", (req, res) => {
    res.send("here!")
});


app.post("/state", upload.single("puzzle"), (req, res) => {
    console.log("Received upload!")

    console.log("File:")
    console.log(req.file)

    console.log("Other data:")
    console.log(req.body)

    res.status(200).json({
        message: "Data received",
        file: req.file?.originalname,
        body: req.body
    })
})
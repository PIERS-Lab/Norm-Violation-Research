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
// Tells the server to check and parse json files whenever a request come in
const path = require("path")
let currentOrder = null;
app.use(cors({
  origin: ['http://localhost:5173', 'http://localhost:5174', 'http://10.248.13.162:5173', 'http://10.248.13.162:5174']
}));
app.use(express.json());
// tells the server to look through the given directory when someone makes a request of that type
app.use("/puzzles", express.static(path.join(__dirname, "uploads")));
// tells the server what to do when recieving data, empty means it'll only run on startup.

app.use((req, res, next) => {
    // console.log("incoming request", req.method, req.url);
    next();
});

app.get("/", (req, res) =>{
    res.send("Hello!")
});

app.get("/state", (req, res) => {
    res.json(currentOrder)
});

app.post("/state", upload.single("puzzle"), (req, res) => {
    console.log("Received upload!")

    console.log("File:")
    console.log(req.file)

    console.log("Other data:")
    console.log(req.body)
    img = req.file
    currentOrder = {
        message: "Data received",
        img_url: `/puzzles/${req.file.filename}`,
        // body containes lscore, rscore, and hscore
        body: req.body
    }
    res.status(200).json(currentOrder)
})

app.listen(3000, () => {console.log("server running!");});
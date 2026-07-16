const express = require("express");
const { chatWithDataset } = require("../controllers/chatController");

const router = express.Router();

router.post("/", chatWithDataset);

module.exports = router;

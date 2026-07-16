const express = require("express");
const { generateChart } = require("../controllers/chartController");

const router = express.Router();

router.post("/", generateChart);

module.exports = router;

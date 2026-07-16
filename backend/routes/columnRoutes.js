const express = require("express");
const getColumns = require("../services/columnService");

const router = express.Router();

router.post("/", async (req, res) => {
    try {
        const { filePath } = req.body;
        const columns = await getColumns(filePath);
        res.json(columns);
    } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        res.status(500).json({ message });
    }
});

module.exports = router;

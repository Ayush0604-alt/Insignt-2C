const getColumns = require("../services/columnService");
const generateSummary = require("../services/summaryService");
const generateRecommendations = require("../services/recommendationService");

const uploadFile = async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: "No file uploaded" });
        }

        const filePath = req.file.path;

        // Run column extraction + summary + recommendations in parallel
        const [columns, summary, recommendations] = await Promise.all([
            getColumns(filePath),
            generateSummary(filePath),
            generateRecommendations(filePath),
        ]);

        res.status(200).json({
            message: "File uploaded successfully",
            filePath,
            columns,
            summary,
            recommendations,
        });

    } catch (error) {
        console.error("[fileController] Upload error:", error);

        const message = error instanceof Error ? error.message : String(error);
        res.status(500).json({ message });
    }
};

module.exports = { uploadFile };
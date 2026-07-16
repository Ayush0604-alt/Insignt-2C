const runPythonScript     = require("../services/pythonRunner");
const generateSummary     = require("../services/summaryService");
const generateCleaningReport = require("../services/cleaningService");
const cleanDataset        = require("../services/datasetCleaningService");
const generateInsights    = require("../services/insightService");
const path                = require("path");

const generateChart = async (req, res) => {
    try {
        const {
            filePath,
            chartType,
            xColumn,
            yColumn,
            removeDuplicates,
            dropMissing,
            missingStrategy,
            chartColor,
            bins,
        } = req.body;

        // Basic validation
        if (!filePath) {
            return res.status(400).json({ message: "No file path provided" });
        }

        if (!chartType) {
            return res.status(400).json({ message: "No chart type provided" });
        }

        // Step 1: Clean dataset
        const finalFilePath = await cleanDataset(
            filePath,
            removeDuplicates,
            dropMissing,
            missingStrategy
        );

        // Step 2: Generate chart — now passes color + bins
        const filename = await runPythonScript(
            finalFilePath,
            chartType,
            xColumn,
            yColumn,
            chartColor || "orange",
            bins || 20
        );

        // Step 3: Generate summary (run in parallel with cleaning report + insights)
        const [summary, cleaningReport, insights] = await Promise.all([
            generateSummary(finalFilePath),
            generateCleaningReport(filePath),
            generateInsights(finalFilePath),
        ]);

        const cleanedFilename = path.basename(finalFilePath);
        const baseUrl = `${req.protocol}://${req.get("host")}`;

        res.status(200).json({
            message:        "Chart generated successfully",
            summary,
            cleaningReport,
            insights,
            cleanedFileUrl: `${baseUrl}/cleaned_data/${cleanedFilename}`,
            imageUrl:       `${baseUrl}/generated_charts/${filename}`,
        });

    } catch (error) {
        console.error("[chartController] Error:", error);

        const message =
            error instanceof Error ? error.message : String(error);

        res.status(500).json({ message });
    }
};

module.exports = { generateChart };
const { resolveScript, runPython } = require("../services/pythonExecutor");

const chatWithDataset = async (req, res) => {
    try {
        const { filePath, query } = req.body;

        if (!filePath) {
            return res.status(400).json({ message: "No file path provided" });
        }
        if (!query) {
            return res.status(400).json({ message: "No query provided" });
        }

        const scriptPath = resolveScript("analysis/chat_agent.py");
        // We pass the dataset path and the user query to the python agent
        const resultText = await runPython(scriptPath, [filePath, query]);

        res.status(200).json({ reply: resultText.trim() });
    } catch (error) {
        console.error("[chatController] Error:", error);
        const message = error instanceof Error ? error.message : String(error);
        res.status(500).json({ message });
    }
};

module.exports = { chatWithDataset };

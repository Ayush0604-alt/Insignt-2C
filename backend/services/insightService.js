const { resolveScript, runPythonJSON } = require("./pythonExecutor");

const SCRIPT_PATH = resolveScript("analysis/insight_generator.py");

/**
 * Generates a list of plain-English insight strings for a dataset.
 * @param {string} filePath
 * @returns {Promise<string[]>}
 */
const generateInsights = (filePath) => runPythonJSON(SCRIPT_PATH, [filePath]);

module.exports = generateInsights;

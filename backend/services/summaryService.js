const { resolveScript, runPythonJSON } = require("./pythonExecutor");

const SCRIPT_PATH = resolveScript("analysis/dataset_summary.py");

/**
 * Generates the full statistical summary (shape, missingness, per-column
 * numeric/categorical stats, top correlations, data quality score).
 * @param {string} filePath
 * @returns {Promise<object>}
 */
const generateSummary = (filePath) => runPythonJSON(SCRIPT_PATH, [filePath]);

module.exports = generateSummary;

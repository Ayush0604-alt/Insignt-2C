const { resolveScript, runPythonJSON } = require("./pythonExecutor");

const SCRIPT_PATH = resolveScript("cleaning/cleaning_report.py");

/**
 * Runs a data-quality check (missing values, duplicates, empty columns,
 * numeric-looking string columns) against the original uploaded file.
 * @param {string} filePath
 * @returns {Promise<object>}
 */
const generateCleaningReport = (filePath) => runPythonJSON(SCRIPT_PATH, [filePath]);

module.exports = generateCleaningReport;

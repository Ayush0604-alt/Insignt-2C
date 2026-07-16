const { resolveScript, runPython } = require("./pythonExecutor");

const SCRIPT_PATH = resolveScript("cleaning/clean_dataset.py");

/**
 * Applies the selected cleaning options and writes a new cleaned CSV.
 * @param {string} filePath
 * @param {boolean|string} removeDuplicates
 * @param {boolean|string} dropMissing
 * @param {string} missingStrategy - "mean" | "median" | "mode" | ""
 * @returns {Promise<string>} Absolute path to the cleaned file
 */
const cleanDataset = (filePath, removeDuplicates, dropMissing, missingStrategy) =>
    runPython(SCRIPT_PATH, [filePath, removeDuplicates, dropMissing, missingStrategy]);

module.exports = cleanDataset;

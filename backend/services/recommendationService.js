const { resolveScript, runPythonJSON } = require("./pythonExecutor");

const SCRIPT_PATH = resolveScript("analysis/chart_recommender.py");

/**
 * Generates suggested chart types for a dataset, each with a reason
 * grounded in the dataset's actual columns/statistics.
 * @param {string} filePath
 * @returns {Promise<{chart: string, reason: string}[]>}
 */
const generateRecommendations = (filePath) => runPythonJSON(SCRIPT_PATH, [filePath]);

module.exports = generateRecommendations;

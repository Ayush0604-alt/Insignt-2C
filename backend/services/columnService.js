const { resolveScript, runPythonJSON } = require("./pythonExecutor");

const SCRIPT_PATH = resolveScript("utils/get_columns.py");

/**
 * Returns all/numeric/categorical column names for a dataset, used to
 * populate the frontend's X/Y column dropdowns.
 * @param {string} filePath
 * @returns {Promise<{all_columns: string[], numeric_columns: string[], categorical_columns: string[]}>}
 */
const getColumns = (filePath) => runPythonJSON(SCRIPT_PATH, [filePath]);

module.exports = getColumns;

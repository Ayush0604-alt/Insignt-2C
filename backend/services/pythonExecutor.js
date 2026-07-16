const { spawn } = require("child_process");
const path = require("path");

/**
 * Previously every service hardcoded "python" as the interpreter and a
 * path like "../python/analysis/dataset_summary.py" that only resolved
 * correctly if the Node process's cwd happened to be backend/. Both of
 * those were silent footguns:
 *   - "python" doesn't exist on most Linux/Mac setups (only "python3" does)
 *   - a relative path breaks the moment the app is started from another directory
 *
 * PYTHON_BIN can be overridden via an environment variable; PYTHON_ROOT
 * is always resolved from this file's own location, so it works
 * regardless of where the process was launched from.
 */
const PYTHON_BIN = process.env.PYTHON_BIN || (process.platform === "win32" ? "python" : "python3");
const PYTHON_ROOT = path.join(__dirname, "..", "..", "python");

/**
 * Resolve a script path relative to the project's python/ directory.
 * @param {string} relativePath - e.g. "analysis/dataset_summary.py"
 * @returns {string} Absolute path to the script
 */
const resolveScript = (relativePath) => path.join(PYTHON_ROOT, relativePath);

/**
 * Spawn a Python script, collect its stdout/stderr, and resolve with
 * trimmed stdout on a clean exit. This is the one place that owns
 * child_process wiring — every service below is a thin, declarative
 * wrapper around it instead of repeating this ~25-line block itself.
 *
 * @param {string} scriptPath - Absolute path to the .py file (use resolveScript)
 * @param {(string|number|boolean)[]} args - Arguments to pass to the script
 * @returns {Promise<string>} Resolves with trimmed stdout
 */
const runPython = (scriptPath, args = []) => {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn(PYTHON_BIN, [scriptPath, ...args.map(String)]);

        let stdout = "";
        let stderr = "";

        pythonProcess.stdout.on("data", (data) => {
            stdout += data.toString();
        });

        pythonProcess.stderr.on("data", (data) => {
            stderr += data.toString();
        });

        pythonProcess.on("close", (code) => {
            if (code === 0) {
                resolve(stdout.trim());
            } else {
                reject(new Error(stderr.trim() || stdout.trim() || `Python exited with code ${code}`));
            }
        });

        pythonProcess.on("error", (err) => {
            reject(new Error(`Failed to start Python ("${PYTHON_BIN}"): ${err.message}`));
        });
    });
};

/**
 * Same as runPython, but parses stdout as JSON. Used by every script
 * that prints a JSON object/array as its final line.
 */
const runPythonJSON = async (scriptPath, args = []) => {
    const output = await runPython(scriptPath, args);
    try {
        return JSON.parse(output);
    } catch {
        throw new Error(`Failed to parse Python output as JSON: ${output}`);
    }
};

module.exports = { PYTHON_BIN, PYTHON_ROOT, resolveScript, runPython, runPythonJSON };

const { resolveScript, runPython } = require("./pythonExecutor");

const CHART_SCRIPTS = {
    histogram: resolveScript("visualization/histogram.py"),
    bar:       resolveScript("visualization/bar_chart.py"),
    pie:       resolveScript("visualization/pie_chart.py"),
    scatter:   resolveScript("visualization/scatter_plot.py"),
    heatmap:   resolveScript("visualization/heatmap.py"),
    boxplot:   resolveScript("visualization/boxplot.py"),
};

/**
 * Build the CLI args for a given chart type. Each script has a slightly
 * different signature, so this keeps that mapping in one readable place
 * instead of scattering it across services.
 */
const buildArgs = (chartType, { filePath, xColumn, yColumn, chartColor, bins }) => {
    switch (chartType) {
        case "histogram":
            // histogram.py filePath xColumn color bins
            return [filePath, xColumn || "", chartColor || "orange", String(bins || 20)];

        case "bar":
            // bar_chart.py filePath xColumn yColumn color
            return [filePath, xColumn || "", yColumn || "", chartColor || "orange"];

        case "scatter":
            // scatter_plot.py filePath xColumn yColumn color
            return [filePath, xColumn || "", yColumn || "", chartColor || "orange"];

        case "boxplot":
            // boxplot.py filePath xColumn groupByColumn(optional) color
            return [filePath, xColumn || "", yColumn || "", chartColor || "orange"];

        case "heatmap":
            // heatmap.py filePath color
            return [filePath, chartColor || "orange"];

        case "pie":
            // pie_chart.py filePath xColumn
            return [filePath, xColumn || ""];

        default:
            return [filePath, xColumn || "", yColumn || ""];
    }
};

/**
 * Run a Python visualization script for the requested chart type.
 * @param {string} filePath  - Absolute path to cleaned dataset
 * @param {string} chartType - One of: histogram | bar | pie | scatter | heatmap | boxplot
 * @param {string} xColumn   - X-axis column name
 * @param {string} yColumn   - Y-axis column name (optional; also used as the
 *                              "group by" column for boxplot)
 * @param {string} chartColor - Color name (orange | blue | green | red | ...)
 * @param {number|string} bins - Number of bins for histogram
 * @returns {Promise<string>} Resolves with the generated chart's filename
 */
const runPythonScript = async (filePath, chartType, xColumn, yColumn, chartColor = "orange", bins = 20) => {
    const scriptPath = CHART_SCRIPTS[chartType];

    if (!scriptPath) {
        throw new Error(`Invalid chart type: ${chartType}`);
    }

    const args = buildArgs(chartType, { filePath, xColumn, yColumn, chartColor, bins });
    const output = await runPython(scriptPath, args);

    if (!output) {
        throw new Error("Python script produced no output");
    }

    return output;
};

module.exports = runPythonScript;

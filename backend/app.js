require("dotenv").config({ path: require("path").join(__dirname, "../.env") });
const express      = require("express");
const cors         = require("cors");
const path         = require("path");

const fileRoutes   = require("./routes/fileRoutes");
const chartRoutes  = require("./routes/chartRoutes");
const columnRoutes = require("./routes/columnRoutes");
const chatRoutes   = require("./routes/chatRoutes");

const app = express();

app.set("trust proxy", true);

// ── Security headers ──────────────────────────────────────
app.use((req, res, next) => {
    res.setHeader("X-Content-Type-Options", "nosniff");
    res.setHeader("X-Frame-Options", "DENY");
    res.setHeader("X-XSS-Protection", "1; mode=block");
    next();
});

// ── Core middleware ───────────────────────────────────────
app.use(cors());
app.use(express.json({ limit: "1mb" }));
app.use(express.urlencoded({ extended: true, limit: "1mb" }));

// ── Static: frontend ─────────────────────────────────────
app.use(express.static(path.join(__dirname, "../frontend")));

// ── Static: generated files ───────────────────────────────
app.use("/generated_charts", express.static(path.join(__dirname, "generated_charts")));
app.use("/cleaned_data",     express.static(path.join(__dirname, "cleaned_data")));
app.use("/uploads",          express.static(path.join(__dirname, "uploads")));

// ── Main route ────────────────────────────────────────────
app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "../frontend/pages/upload.html"));
});

// ── API routes ────────────────────────────────────────────
app.use("/api/upload-file",    fileRoutes);
app.use("/api/generate-chart", chartRoutes);
app.use("/api/columns",        columnRoutes);
app.use("/api/chat",           chatRoutes);

// ── 404 handler ───────────────────────────────────────────
app.use((req, res) => {
    res.status(404).json({ message: "Route not found" });
});

// ── Global error handler ──────────────────────────────────
app.use((err, req, res, next) => {
    console.error("[app] Unhandled error:", err);

    // Multer file-size error
    if (err.code === "LIMIT_FILE_SIZE") {
        return res.status(413).json({ message: "File too large. Maximum size is 50 MB." });
    }

    const message = err instanceof Error ? err.message : "Internal server error";
    res.status(500).json({ message });
});

module.exports = app;
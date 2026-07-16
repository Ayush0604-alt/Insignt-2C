const multer = require("multer");
const path   = require("path");
const fs     = require("fs");

const UPLOAD_PATH    = path.join(__dirname, "../uploads");
const ALLOWED_TYPES  = [".csv", ".xlsx", ".json"];
const MAX_SIZE_BYTES = 50 * 1024 * 1024; // 50 MB

// Ensure uploads folder exists
if (!fs.existsSync(UPLOAD_PATH)) {
    fs.mkdirSync(UPLOAD_PATH, { recursive: true });
}

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, UPLOAD_PATH),

    filename: (req, file, cb) => {
        // Sanitize original filename, keep extension
        const ext      = path.extname(file.originalname).toLowerCase();
        const safeName = `${Date.now()}_${Math.random().toString(36).slice(2, 8)}${ext}`;
        cb(null, safeName);
    },
});

const fileFilter = (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();

    if (ALLOWED_TYPES.includes(ext)) {
        cb(null, true);
    } else {
        cb(new Error(`Only ${ALLOWED_TYPES.join(", ")} files are allowed`), false);
    }
};

const upload = multer({
    storage,
    fileFilter,
    limits: { fileSize: MAX_SIZE_BYTES },
});

module.exports = upload;
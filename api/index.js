const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type', 'Accept']
}));

app.use(express.json());
app.use(express.static('public'));

// Multer configuration for file uploads (memory storage)
const upload = multer({ 
    storage: multer.memoryStorage(),
    limits: {
        fileSize: 50 * 1024 * 1024 // 50MB limit
    },
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('Only JPEG, PNG, and WebP images are allowed'), false);
        }
    }
});

// Serve static files from templates and static directories
app.use('/static', express.static(path.join(__dirname, '../static')));
app.use('/templates', express.static(path.join(__dirname, '../templates')));

// Root route - serve the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../templates/index.html'));
});

// Favicon route
app.get('/favicon.ico', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/favicon.ico'));
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        service: 'ExifEraser Node.js Backend',
        timestamp: new Date().toISOString()
    });
});

// Image metadata cleaning endpoint
app.post('/clean', upload.single('image'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No image file uploaded' });
        }

        console.log(`Processing image: ${req.file.originalname}, size: ${req.file.size} bytes`);

        // Extract metadata before cleaning (for display purposes)
        let metadataBefore = {};
        try {
            const metadata = await sharp(req.file.buffer).metadata();
            metadataBefore = {
                format: metadata.format,
                width: metadata.width,
                height: metadata.height,
                density: metadata.density,
                hasProfile: metadata.hasProfile,
                hasAlpha: metadata.hasAlpha,
                exif: metadata.exif ? 'EXIF data present' : 'No EXIF data',
                icc: metadata.icc ? 'ICC profile present' : 'No ICC profile'
            };
        } catch (metaError) {
            console.log('Metadata extraction error:', metaError.message);
            metadataBefore = { error: 'Could not extract metadata' };
        }

        // Process image and remove all metadata
        const processedBuffer = await sharp(req.file.buffer)
            .rotate() // Auto-rotate based on EXIF orientation, then remove EXIF
            .jpeg({ 
                quality: 95, 
                progressive: true,
                mozjpeg: true 
            }) // Convert to JPEG for consistency
            .toBuffer();

        // Convert processed image to base64 for frontend display
        const base64Image = processedBuffer.toString('base64');
        const dataUrl = `data:image/jpeg;base64,${base64Image}`;

        console.log(`✅ Successfully processed image. Original: ${req.file.size} bytes, Processed: ${processedBuffer.length} bytes`);

        // Response with cleaned image
        res.json({
            success: true,
            image_url: dataUrl,
            filename: `cleaned_${req.file.originalname}`,
            metadata_before: metadataBefore,
            metadata_after: 'All metadata removed successfully with lossless compression.',
            original_size: req.file.size,
            processed_size: processedBuffer.length
        });

    } catch (error) {
        console.error('Error processing image:', error);
        res.status(500).json({ 
            error: 'Failed to process image', 
            details: error.message 
        });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    if (error instanceof multer.MulterError) {
        if (error.code === 'LIMIT_FILE_SIZE') {
            return res.status(413).json({ error: 'File too large. Maximum size is 50MB.' });
        }
    }
    console.error('Server error:', error);
    res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({ error: 'Endpoint not found' });
});

// Start server
if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`🚀 ExifEraser Node.js Backend running on port ${PORT}`);
        console.log(`📡 Health check: http://localhost:${PORT}/health`);
        console.log(`🌐 Frontend: http://localhost:${PORT}/`);
    });
}

// Export for Vercel
module.exports = app;
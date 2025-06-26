# FIDC Analysis Dashboard

A modern React frontend with Node.js backend for CSV analysis and fund comparison. This web interface integrates with the existing Python analysis tools to provide an easy-to-use dashboard for data analysis.

## Features

- **CSV File Comparison**: Upload two CSV files and compare them using the advanced comparison engine
- **Fund Analysis**: Upload fund position reports and analyze against internal data
- **Real-time Progress**: Live updates during analysis with detailed progress tracking
- **Multiple Output Formats**: Support for HTML, Excel, CSV, and Google Sheets exports
- **Interactive Results**: View HTML reports directly in the browser or download files
- **Responsive Design**: Modern, mobile-friendly interface built with Tailwind CSS

## Architecture

```
frontend/
├── server/              # Node.js Express backend
│   ├── package.json
│   ├── server.js       # Main server with API endpoints
│   └── uploads/        # Temporary file storage
└── client/             # React frontend
    ├── package.json
    ├── src/
    │   ├── components/ # Reusable UI components
    │   ├── pages/      # Main application pages
    │   ├── utils/      # API utilities and helpers
    │   └── App.js      # Main application component
    └── public/         # Static assets
```

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+ with the existing FIDC analysis tools set up
- All Python dependencies from the main project installed

## Installation

### 1. Install Backend Dependencies

```bash
cd frontend/server
npm install
```

### 2. Install Frontend Dependencies

```bash
cd frontend/client
npm install
```

## Running the Application

### Development Mode

1. **Start the Backend Server** (in one terminal):
   ```bash
   cd frontend/server
   npm run dev
   ```
   The API server will start on http://localhost:5000

2. **Start the Frontend Development Server** (in another terminal):
   ```bash
   cd frontend/client
   npm start
   ```
   The React app will start on http://localhost:3000

### Production Mode

1. **Build the Frontend**:
   ```bash
   cd frontend/client
   npm run build
   ```

2. **Start the Production Server**:
   ```bash
   cd frontend/server
   npm start
   ```

## How It Works

### Integration with Python Tools

The web dashboard seamlessly integrates with your existing Python analysis tools:

1. **CSV Comparison**: 
   - Uses `cli/csv_compare_cli.py` for general CSV file comparison
   - Supports all existing comparison features and output formats

2. **Fund Analysis**:
   - Uses `scripts/run_fund_analysis.py` for fund-specific analysis
   - Includes BigQuery data extraction and comprehensive reporting
   - Supports PI and AI funds with configurable reference dates

### API Endpoints

- `POST /api/upload-and-analyze` - Upload two files for CSV comparison
- `POST /api/upload-fund-analysis` - Upload fund file for analysis
- `GET /api/analysis/:jobId` - Get analysis status
- `GET /api/results/:jobId` - Get analysis results
- `GET /api/download/:jobId` - Download result files

### Analysis Process

1. **File Upload**: Files are uploaded and stored temporarily
2. **Job Creation**: Each analysis gets a unique job ID for tracking
3. **Python Execution**: The appropriate Python script is executed with uploaded files
4. **Progress Tracking**: Real-time status updates via polling
5. **Results Display**: Interactive results with download options

## Usage Guide

### CSV File Comparison

1. Navigate to the **CSV Comparison** tab
2. Upload two CSV files using drag-and-drop or file picker
3. Select your preferred output format (HTML, JSON, or CSV)
4. Click "Start Comparison Analysis"
5. Monitor progress on the results page
6. View or download the comparison report

### Fund Analysis

1. Navigate to the **Fund Analysis** tab
2. Upload a fund position report (CSV format)
3. Select the fund type (PI or AI)
4. Set the reference date for internal data extraction
5. Choose output format (Excel, CSV, or Google Sheets)
6. Click "Start Fund Analysis"
7. Monitor progress and download results when complete

## Configuration

### Environment Variables

Create a `.env` file in the `frontend/server` directory:

```bash
PORT=5000
NODE_ENV=development
# Add other configuration as needed
```

### Python Integration

The backend automatically calls the Python scripts from the project root. Ensure:

- Python is available in the system PATH
- All required Python packages are installed
- BigQuery credentials are configured for fund analysis
- Google Sheets credentials are set up if using Google Sheets export

## Troubleshooting

### Common Issues

1. **Python script errors**: Check that all Python dependencies are installed and working
2. **File upload issues**: Ensure the uploads directory has proper permissions
3. **BigQuery access**: Verify BigQuery credentials for fund analysis
4. **Port conflicts**: Change the PORT environment variable if needed

### Debug Mode

Enable debug logging by setting `NODE_ENV=development` in the server environment.

## File Processing

- **Upload Limit**: 50MB per file
- **Supported Formats**: CSV files only
- **Temporary Storage**: Files are automatically cleaned up after processing
- **Job Retention**: Analysis jobs are cleaned up after 1 hour

## Security Considerations

- Files are stored temporarily and cleaned up automatically
- No authentication currently implemented (add as needed)
- CORS is enabled for development (configure for production)
- Input validation on file types and sizes

## Development

### Adding New Analysis Types

1. Add new API endpoint in `server.js`
2. Create corresponding Python script integration
3. Add new UI components and pages in the React app
4. Update the routing and navigation

### Extending the UI

The frontend uses:
- **React 18** with functional components and hooks
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API communication
- **Lucide React** for icons

## Production Deployment

For production deployment:

1. Build the React app: `npm run build`
2. Serve static files from the Express server
3. Set up proper environment variables
4. Configure reverse proxy (nginx/Apache) if needed
5. Set up process management (PM2, systemd, etc.)
6. Configure SSL/HTTPS
7. Set up proper logging and monitoring

## Integration with Existing Tools

This web dashboard is designed to work seamlessly with your existing Python analysis infrastructure:

- Reuses all existing comparison algorithms and logic
- Maintains compatibility with current data processing pipelines
- Leverages existing BigQuery connections and credentials
- Supports all current output formats and reporting features

You can continue using the command-line tools alongside the web interface without any conflicts. 
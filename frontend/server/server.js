const express = require('express');
const multer = require('multer');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs-extra');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, 'uploads');
fs.ensureDirSync(uploadsDir);

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/csv' || file.originalname.endsWith('.csv')) {
      cb(null, true);
    } else {
      cb(new Error('Only CSV files are allowed!'), false);
    }
  }
});

// Store analysis jobs
const analysisJobs = new Map();

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'Server is running' });
});

// Upload files and start analysis
app.post('/api/upload-and-analyze', upload.fields([
  { name: 'file1', maxCount: 1 },
  { name: 'file2', maxCount: 1 }
]), async (req, res) => {
  try {
    const { analysisType = 'general', outputFormat = 'html' } = req.body;
    
    if (!req.files || !req.files.file1 || !req.files.file2) {
      return res.status(400).json({ 
        error: 'Both files are required',
        details: 'Please upload two CSV files for comparison'
      });
    }

    const file1 = req.files.file1[0];
    const file2 = req.files.file2[0];
    const jobId = uuidv4();
    
    // Store job info
    analysisJobs.set(jobId, {
      id: jobId,
      status: 'processing',
      startTime: new Date(),
      files: {
        file1: file1.filename,
        file2: file2.filename
      },
      analysisType,
      outputFormat,
      progress: 0
    });

    // Start analysis in background
    runAnalysis(jobId, file1.path, file2.path, analysisType, outputFormat);
    
    res.json({
      jobId,
      message: 'Analysis started',
      files: {
        file1: file1.originalname,
        file2: file2.originalname
      }
    });

  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ 
      error: 'Upload failed',
      details: error.message 
    });
  }
});

// Upload files for fund analysis
app.post('/api/upload-fund-analysis', upload.single('fundFile'), async (req, res) => {
  try {
    const { fundAlias = 'pi', referenceDate = '2025-05-30', outputFormat = 'excel' } = req.body;
    
    if (!req.file) {
      return res.status(400).json({ 
        error: 'Fund file is required',
        details: 'Please upload a CSV file for fund analysis'
      });
    }

    const jobId = uuidv4();
    
    // Store job info
    analysisJobs.set(jobId, {
      id: jobId,
      status: 'processing',
      startTime: new Date(),
      files: {
        fundFile: req.file.filename
      },
      analysisType: 'fund',
      fundAlias,
      referenceDate,
      outputFormat,
      progress: 0
    });

    // Start fund analysis in background
    runFundAnalysis(jobId, req.file.path, fundAlias, referenceDate, outputFormat);
    
    res.json({
      jobId,
      message: 'Fund analysis started',
      file: req.file.originalname,
      fundAlias,
      referenceDate
    });

  } catch (error) {
    console.error('Fund analysis upload error:', error);
    res.status(500).json({ 
      error: 'Upload failed',
      details: error.message 
    });
  }
});

// Get analysis status
app.get('/api/analysis/:jobId', (req, res) => {
  const { jobId } = req.params;
  const job = analysisJobs.get(jobId);
  
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  res.json(job);
});

// Get analysis results
app.get('/api/results/:jobId', async (req, res) => {
  const { jobId } = req.params;
  const job = analysisJobs.get(jobId);
  
  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }
  
  if (job.status !== 'completed') {
    return res.status(202).json({ 
      message: 'Analysis not completed yet',
      status: job.status 
    });
  }
  
  try {
    // Return the results file path or content
    if (job.resultFile) {
      const resultPath = path.join(__dirname, '..', '..', job.resultFile);
      if (await fs.pathExists(resultPath)) {
        if (job.outputFormat === 'html') {
          const htmlContent = await fs.readFile(resultPath, 'utf8');
          res.json({ 
            type: 'html',
            content: htmlContent,
            downloadUrl: `/api/download/${jobId}`
          });
        } else {
          res.json({
            type: 'file',
            downloadUrl: `/api/download/${jobId}`,
            filename: path.basename(resultPath)
          });
        }
      } else {
        res.status(404).json({ error: 'Result file not found' });
      }
    } else {
      res.json({ 
        message: 'Analysis completed but no result file generated',
        logs: job.logs 
      });
    }
  } catch (error) {
    console.error('Error reading results:', error);
    res.status(500).json({ error: 'Failed to read results' });
  }
});

// Download results file
app.get('/api/download/:jobId', async (req, res) => {
  const { jobId } = req.params;
  const job = analysisJobs.get(jobId);
  
  if (!job || !job.resultFile) {
    return res.status(404).json({ error: 'File not found' });
  }
  
  try {
    const resultPath = path.join(__dirname, '..', '..', job.resultFile);
    if (await fs.pathExists(resultPath)) {
      res.download(resultPath, path.basename(resultPath));
    } else {
      res.status(404).json({ error: 'File not found' });
    }
  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({ error: 'Download failed' });
  }
});

// Clean up old jobs (run every hour)
setInterval(() => {
  const now = new Date();
  for (const [jobId, job] of analysisJobs.entries()) {
    const age = now - job.startTime;
    if (age > 3600000) { // 1 hour
      analysisJobs.delete(jobId);
    }
  }
}, 3600000);

// Analysis functions
function runAnalysis(jobId, file1Path, file2Path, analysisType, outputFormat) {
  const job = analysisJobs.get(jobId);
  const projectRoot = path.join(__dirname, '..', '..');
  
  // Use the CLI tool for general CSV comparison
  const pythonScript = path.join(projectRoot, 'cli', 'csv_compare_cli.py');
  const args = [
    pythonScript,
    'compare',
    file1Path,
    file2Path,
    '--format', outputFormat
  ];
  
  console.log(`Starting analysis for job ${jobId}`);
  console.log(`Command: python ${args.join(' ')}`);
  
  const pythonProcess = spawn('python', args, {
    cwd: projectRoot,
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  let stdout = '';
  let stderr = '';
  
  pythonProcess.stdout.on('data', (data) => {
    stdout += data.toString();
    console.log(`Job ${jobId} stdout:`, data.toString());
  });
  
  pythonProcess.stderr.on('data', (data) => {
    stderr += data.toString();
    console.error(`Job ${jobId} stderr:`, data.toString());
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`Job ${jobId} finished with code ${code}`);
    
    if (code === 0) {
      job.status = 'completed';
      job.progress = 100;
      job.logs = stdout;
      
      // Find the generated report file
      const reportsDir = path.join(projectRoot, 'reports', 'comparisons');
      findLatestReportFile(reportsDir, outputFormat)
        .then(reportFile => {
          if (reportFile) {
            job.resultFile = path.relative(projectRoot, reportFile);
          }
        })
        .catch(err => console.error('Error finding report file:', err));
        
    } else {
      job.status = 'failed';
      job.error = stderr || 'Analysis failed';
      job.logs = stdout;
    }
    
    job.endTime = new Date();
  });
  
  pythonProcess.on('error', (error) => {
    console.error(`Job ${jobId} error:`, error);
    job.status = 'failed';
    job.error = error.message;
    job.endTime = new Date();
  });
}

function runFundAnalysis(jobId, fundFilePath, fundAlias, referenceDate, outputFormat) {
  const job = analysisJobs.get(jobId);
  const projectRoot = path.join(__dirname, '..', '..');
  
  // Copy the uploaded file to the data directory with the expected naming
  const dataDir = path.join(projectRoot, 'data');
  const targetFileName = `uploaded_fund_${fundAlias}_${Date.now()}.csv`;
  const targetPath = path.join(dataDir, targetFileName);
  
  fs.copy(fundFilePath, targetPath)
    .then(() => {
      // Use the fund analysis script
      const pythonScript = path.join(projectRoot, 'scripts', 'run_fund_analysis.py');
      const args = [
        pythonScript,
        '--fund', fundAlias,
        '--date', referenceDate,
        '--format', outputFormat,
        '--output-only'
      ];
      
      console.log(`Starting fund analysis for job ${jobId}`);
      console.log(`Command: python ${args.join(' ')}`);
      
      const pythonProcess = spawn('python', args, {
        cwd: projectRoot,
        stdio: ['pipe', 'pipe', 'pipe']
      });
      
      let stdout = '';
      let stderr = '';
      
      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
        console.log(`Job ${jobId} stdout:`, data.toString());
      });
      
      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        console.error(`Job ${jobId} stderr:`, data.toString());
      });
      
      pythonProcess.on('close', (code) => {
        console.log(`Job ${jobId} finished with code ${code}`);
        
        if (code === 0) {
          job.status = 'completed';
          job.progress = 100;
          job.logs = stdout;
          
          // Find the generated report file
          const reportsDir = path.join(projectRoot, 'reports', 'formatted_exports');
          findLatestReportFile(reportsDir, outputFormat)
            .then(reportFile => {
              if (reportFile) {
                job.resultFile = path.relative(projectRoot, reportFile);
              }
            })
            .catch(err => console.error('Error finding report file:', err));
            
        } else {
          job.status = 'failed';
          job.error = stderr || 'Fund analysis failed';
          job.logs = stdout;
        }
        
        job.endTime = new Date();
        
        // Clean up uploaded file
        fs.unlink(targetPath).catch(err => console.error('Error cleaning up file:', err));
      });
      
      pythonProcess.on('error', (error) => {
        console.error(`Job ${jobId} error:`, error);
        job.status = 'failed';
        job.error = error.message;
        job.endTime = new Date();
        
        // Clean up uploaded file
        fs.unlink(targetPath).catch(err => console.error('Error cleaning up file:', err));
      });
    })
    .catch(error => {
      console.error(`Error copying fund file for job ${jobId}:`, error);
      job.status = 'failed';
      job.error = 'Failed to process uploaded file';
      job.endTime = new Date();
    });
}

async function findLatestReportFile(dir, format) {
  try {
    if (!await fs.pathExists(dir)) {
      return null;
    }
    
    const files = await fs.readdir(dir);
    const extension = format === 'html' ? '.html' : (format === 'excel' ? '.xlsx' : '.csv');
    const reportFiles = files.filter(f => f.endsWith(extension));
    
    if (reportFiles.length === 0) {
      return null;
    }
    
    // Get the most recent file
    const fileStats = await Promise.all(
      reportFiles.map(async f => ({
        name: f,
        path: path.join(dir, f),
        mtime: (await fs.stat(path.join(dir, f))).mtime
      }))
    );
    
    fileStats.sort((a, b) => b.mtime - a.mtime);
    return fileStats[0].path;
    
  } catch (error) {
    console.error('Error finding latest report file:', error);
    return null;
  }
}

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/api/health`);
}); 
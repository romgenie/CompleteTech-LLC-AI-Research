import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Article as ArticleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

/**
 * Dialog for uploading papers with validation and multiple files support
 * 
 * @component
 */
const PaperUploadDialog = ({
  open,
  onClose,
  onUpload,
  maxFiles = 5
}) => {
  // State
  const [activeStep, setActiveStep] = useState(0);
  const [files, setFiles] = useState([]);
  const [fileErrors, setFileErrors] = useState({});
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadResults, setUploadResults] = useState({});
  const [paperDetails, setPaperDetails] = useState({});
  const [uploadError, setUploadError] = useState(null);
  
  // Steps in the upload process
  const steps = ['Select Files', 'Enter Details', 'Upload & Process'];
  
  // Handle file selection
  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const newErrors = {};
    
    // Validate file types and sizes
    const validFiles = selectedFiles.filter(file => {
      const isPDF = file.type === 'application/pdf';
      const isWithinSize = file.size <= 15 * 1024 * 1024; // 15MB max
      
      if (!isPDF) {
        newErrors[file.name] = 'Only PDF files are supported';
      } else if (!isWithinSize) {
        newErrors[file.name] = 'File must be under 15MB';
      }
      
      return isPDF && isWithinSize;
    });
    
    // Limit number of files
    const finalFiles = [...files, ...validFiles].slice(0, maxFiles);
    
    setFiles(finalFiles);
    setFileErrors(newErrors);
    
    // Initialize paper details for new files
    const newPaperDetails = { ...paperDetails };
    finalFiles.forEach(file => {
      if (!newPaperDetails[file.name]) {
        newPaperDetails[file.name] = {
          title: file.name.replace(/\.pdf$/i, ''),
          authors: '',
          year: new Date().getFullYear().toString(),
          abstract: ''
        };
      }
    });
    setPaperDetails(newPaperDetails);
  };
  
  // Handle removing a file
  const handleRemoveFile = (filename) => {
    setFiles(files.filter(file => file.name !== filename));
    
    // Clean up related state
    const newFileErrors = { ...fileErrors };
    delete newFileErrors[filename];
    setFileErrors(newFileErrors);
    
    const newPaperDetails = { ...paperDetails };
    delete newPaperDetails[filename];
    setPaperDetails(newPaperDetails);
    
    const newUploadProgress = { ...uploadProgress };
    delete newUploadProgress[filename];
    setUploadProgress(newUploadProgress);
    
    const newUploadResults = { ...uploadResults };
    delete newUploadResults[filename];
    setUploadResults(newUploadResults);
  };
  
  // Handle updating paper details
  const handlePaperDetailsChange = (filename, field, value) => {
    setPaperDetails(prev => ({
      ...prev,
      [filename]: {
        ...prev[filename],
        [field]: value
      }
    }));
  };
  
  // Handle next step
  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      // Final step - upload files
      handleUpload();
    } else {
      setActiveStep(prevStep => prevStep + 1);
    }
  };
  
  // Handle back step
  const handleBack = () => {
    setActiveStep(prevStep => prevStep - 1);
  };
  
  // Handle dialog close
  const handleClose = () => {
    // Reset state
    setActiveStep(0);
    setFiles([]);
    setFileErrors({});
    setUploadProgress({});
    setUploadResults({});
    setPaperDetails({});
    setUploadError(null);
    
    // Call onClose
    onClose();
  };
  
  // Handle file upload
  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploadError(null);
    
    try {
      // Upload each file with its details
      const results = {};
      
      for (const file of files) {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: 0
        }));
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', paperDetails[file.name].title);
        formData.append('authors', paperDetails[file.name].authors);
        formData.append('year', paperDetails[file.name].year);
        formData.append('abstract', paperDetails[file.name].abstract);
        
        try {
          // Simulated upload with progress
          const result = await simulateFileUpload(file, formData, progress => {
            setUploadProgress(prev => ({
              ...prev,
              [file.name]: progress
            }));
          });
          
          results[file.name] = { success: true, data: result };
        } catch (error) {
          results[file.name] = { success: false, error: error.message };
        }
      }
      
      setUploadResults(results);
      
      // Call onUpload with results
      const successfulUploads = Object.entries(results)
        .filter(([_, result]) => result.success)
        .map(([filename, result]) => ({
          filename,
          ...result.data,
          details: paperDetails[filename]
        }));
      
      if (successfulUploads.length > 0) {
        onUpload(successfulUploads);
      }
    } catch (error) {
      setUploadError(error.message || 'Failed to upload files');
    }
  };
  
  // Simulate file upload with progress
  const simulateFileUpload = (file, formData, progressCallback) => {
    return new Promise((resolve, reject) => {
      // In a real implementation, this would be an API call
      // For now, we'll simulate progress and response
      
      const totalSteps = 10;
      let currentStep = 0;
      
      const interval = setInterval(() => {
        currentStep++;
        progressCallback(Math.round((currentStep / totalSteps) * 100));
        
        if (currentStep >= totalSteps) {
          clearInterval(interval);
          
          // Simulate 10% failure rate
          if (Math.random() < 0.1) {
            reject(new Error('Upload failed: Server error'));
          } else {
            // Successful upload
            resolve({
              id: `paper-${Date.now()}-${Math.round(Math.random() * 1000)}`,
              status: 'uploaded',
              uploaded_at: new Date().toISOString(),
              url: 'https://example.com/papers/' + file.name
            });
          }
        }
      }, 200);
    });
  };
  
  // Determine if next button should be disabled
  const isNextDisabled = () => {
    if (activeStep === 0) {
      // File selection step
      return files.length === 0 || Object.keys(fileErrors).length > 0;
    } else if (activeStep === 1) {
      // Paper details step
      return files.some(file => {
        const details = paperDetails[file.name] || {};
        return !details.title || !details.authors || !details.year;
      });
    }
    
    return false;
  };
  
  // Render file selection step
  const renderFileSelectionStep = () => (
    <>
      <DialogContentText>
        Select PDF files to upload. You can upload up to {maxFiles} files at once.
      </DialogContentText>
      
      <Box sx={{ mt: 2, mb: 3 }}>
        <Button
          variant="contained"
          component="label"
          startIcon={<UploadIcon />}
          color="primary"
        >
          Select Files
          <input
            type="file"
            hidden
            accept=".pdf"
            multiple
            onChange={handleFileSelect}
          />
        </Button>
      </Box>
      
      {files.length > 0 && (
        <Paper variant="outlined" sx={{ p: 2, mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Selected Files ({files.length}/{maxFiles})
          </Typography>
          
          <List dense>
            {files.map((file, index) => (
              <React.Fragment key={file.name}>
                {index > 0 && <Divider />}
                <ListItem>
                  <ArticleIcon sx={{ mr: 2, color: 'primary.main' }} />
                  <ListItemText
                    primary={file.name}
                    secondary={`${(file.size / (1024 * 1024)).toFixed(2)} MB`}
                    primaryTypographyProps={{
                      variant: 'body2',
                      style: { fontWeight: fileErrors[file.name] ? 'normal' : 'medium' }
                    }}
                    secondaryTypographyProps={{
                      variant: 'caption',
                      color: fileErrors[file.name] ? 'error' : 'text.secondary'
                    }}
                  />
                  {fileErrors[file.name] && (
                    <Typography variant="caption" color="error" sx={{ ml: 1, flexGrow: 1 }}>
                      {fileErrors[file.name]}
                    </Typography>
                  )}
                  <ListItemSecondaryAction>
                    <IconButton edge="end" onClick={() => handleRemoveFile(file.name)} size="small">
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        </Paper>
      )}
    </>
  );
  
  // Render paper details step
  const renderPaperDetailsStep = () => (
    <>
      <DialogContentText>
        Enter details for each paper. These will be used to enhance the knowledge graph.
      </DialogContentText>
      
      <Box sx={{ mt: 3 }}>
        {files.map((file, index) => (
          <Paper key={file.name} variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              File {index + 1}: {file.name}
            </Typography>
            
            <TextField
              fullWidth
              label="Paper Title"
              margin="dense"
              value={paperDetails[file.name]?.title || ''}
              onChange={(e) => handlePaperDetailsChange(file.name, 'title', e.target.value)}
              required
              error={!paperDetails[file.name]?.title}
              helperText={!paperDetails[file.name]?.title ? 'Title is required' : ''}
            />
            
            <TextField
              fullWidth
              label="Authors (comma-separated)"
              margin="dense"
              value={paperDetails[file.name]?.authors || ''}
              onChange={(e) => handlePaperDetailsChange(file.name, 'authors', e.target.value)}
              required
              error={!paperDetails[file.name]?.authors}
              helperText={!paperDetails[file.name]?.authors ? 'At least one author is required' : ''}
            />
            
            <TextField
              fullWidth
              label="Publication Year"
              margin="dense"
              value={paperDetails[file.name]?.year || ''}
              onChange={(e) => handlePaperDetailsChange(file.name, 'year', e.target.value)}
              required
              error={!paperDetails[file.name]?.year}
              helperText={!paperDetails[file.name]?.year ? 'Year is required' : ''}
              inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
            />
            
            <TextField
              fullWidth
              label="Abstract"
              margin="dense"
              value={paperDetails[file.name]?.abstract || ''}
              onChange={(e) => handlePaperDetailsChange(file.name, 'abstract', e.target.value)}
              multiline
              rows={3}
            />
          </Paper>
        ))}
      </Box>
    </>
  );
  
  // Render upload step
  const renderUploadStep = () => (
    <>
      <DialogContentText>
        Papers are being uploaded and processed. This may take a few minutes.
      </DialogContentText>
      
      {uploadError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {uploadError}
        </Alert>
      )}
      
      <Box sx={{ mt: 3 }}>
        {files.map(file => (
          <Paper key={file.name} variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <ArticleIcon sx={{ mr: 2, color: 'primary.main' }} />
              <Typography variant="body2" sx={{ flexGrow: 1 }}>
                {paperDetails[file.name]?.title || file.name}
              </Typography>
              
              {uploadResults[file.name] ? (
                uploadResults[file.name].success ? (
                  <CheckCircleIcon color="success" />
                ) : (
                  <ErrorIcon color="error" />
                )
              ) : (
                <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress 
                    variant="determinate" 
                    value={uploadProgress[file.name] || 0}
                    size={24}
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography
                      variant="caption"
                      component="div"
                      color="text.secondary"
                      sx={{ fontSize: '0.6rem' }}
                    >
                      {uploadProgress[file.name] || 0}%
                    </Typography>
                  </Box>
                </Box>
              )}
            </Box>
            
            {uploadResults[file.name] && !uploadResults[file.name].success && (
              <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
                Error: {uploadResults[file.name].error}
              </Typography>
            )}
            
            {uploadResults[file.name] && uploadResults[file.name].success && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Paper ID: {uploadResults[file.name].data.id}
              </Typography>
            )}
          </Paper>
        ))}
      </Box>
      
      {/* Show success message if all uploads complete */}
      {files.length > 0 && 
       Object.keys(uploadResults).length === files.length && 
       Object.values(uploadResults).some(result => result.success) && (
        <Alert severity="success" sx={{ mt: 2 }}>
          {Object.values(uploadResults).filter(result => result.success).length} out of {files.length} papers uploaded successfully.
          {Object.values(uploadResults).filter(result => !result.success).length > 0 && 
            ` ${Object.values(uploadResults).filter(result => !result.success).length} failed.`}
        </Alert>
      )}
    </>
  );
  
  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      fullWidth
      maxWidth="md"
      aria-labelledby="paper-upload-dialog-title"
    >
      <DialogTitle id="paper-upload-dialog-title">
        Upload Papers
      </DialogTitle>
      
      <DialogContent>
        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map(label => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        
        {/* Step content */}
        {activeStep === 0 && renderFileSelectionStep()}
        {activeStep === 1 && renderPaperDetailsStep()}
        {activeStep === 2 && renderUploadStep()}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose}>
          {activeStep === steps.length - 1 && 
            Object.keys(uploadResults).length === files.length && 
            Object.values(uploadResults).some(result => result.success)
            ? 'Close' : 'Cancel'}
        </Button>
        
        {activeStep > 0 && activeStep < steps.length - 1 && (
          <Button onClick={handleBack}>
            Back
          </Button>
        )}
        
        {(activeStep < steps.length - 1 || 
          (activeStep === steps.length - 1 && 
           Object.keys(uploadResults).length < files.length)) && (
          <Button 
            onClick={handleNext} 
            variant="contained"
            disabled={isNextDisabled() || 
                      (activeStep === steps.length - 1 && 
                       Object.keys(uploadResults).length > 0 && 
                       Object.keys(uploadResults).length < files.length)}
          >
            {activeStep === steps.length - 1 ? 'Upload' : 'Next'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

PaperUploadDialog.propTypes = {
  /** Whether the dialog is open */
  open: PropTypes.bool.isRequired,
  
  /** Callback when dialog is closed */
  onClose: PropTypes.func.isRequired,
  
  /** Callback when papers are uploaded successfully */
  onUpload: PropTypes.func.isRequired,
  
  /** Maximum number of files allowed */
  maxFiles: PropTypes.number
};

export default PaperUploadDialog;
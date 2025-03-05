import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  List,
  ListItem,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Chip,
  Tab,
  Tabs,
  FormControlLabel,
  Switch,
  Tooltip,
  Divider,
  Alert,
  CircularProgress,
  Snackbar
} from '@mui/material';
import {
  ContentCopy as ContentCopyIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  FileCopy as FileCopyIcon,
  Add as AddIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import citationService from '../services/citationService';
import { CitationPaper, CitationStyle } from '../utils/citationManager';

// Interface for props
interface CitationManagerProps {
  researchResults?: any[];
  onCite?: (citation: string, style: CitationStyle) => void;
}

// Interface for tab panel props
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// Component for tab panel
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`citation-tabpanel-${index}`}
      aria-labelledby={`citation-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

/**
 * Citation Manager component for managing and generating citations in various formats
 */
const CitationManager: React.FC<CitationManagerProps> = ({ researchResults, onCite }) => {
  // Component state
  const [papers, setPapers] = useState<CitationPaper[]>([]);
  const [selectedPaper, setSelectedPaper] = useState<CitationPaper | null>(null);
  const [citationStyle, setCitationStyle] = useState<CitationStyle>('APA');
  const [formattedCitation, setFormattedCitation] = useState<string>('');
  const [bibliography, setBibliography] = useState<string>('');
  const [exportFormat, setExportFormat] = useState<'txt' | 'html' | 'bibtex'>('txt');
  const [isAddDialogOpen, setIsAddDialogOpen] = useState<boolean>(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState<boolean>(false);
  const [isPreferencesDialogOpen, setIsPreferencesDialogOpen] = useState<boolean>(false);
  const [tabValue, setTabValue] = useState<number>(0);
  const [newPaper, setNewPaper] = useState<Partial<CitationPaper>>({
    title: '',
    authors: [''],
    year: ''
  });
  const [includeAbstract, setIncludeAbstract] = useState<boolean>(false);
  const [lookupUrl, setLookupUrl] = useState<string>('');
  const [isLookupDialogOpen, setIsLookupDialogOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    // Load citation preferences
    const loadPreferences = async () => {
      try {
        const prefs = await citationService.getPreferences();
        setCitationStyle(prefs.defaultStyle);
        setIncludeAbstract(prefs.includeAbstract);
        setExportFormat(prefs.defaultFormat);
      } catch (err) {
        console.error('Error loading citation preferences:', err);
      }
    };

    loadPreferences();

    // If research results are provided, add them to the citation manager
    if (researchResults && researchResults.length > 0) {
      const manager = citationService.createManagerFromResults(researchResults);
      setPapers(manager.getAllPapers());
    }

    // Load any existing papers from the citation service
    setPapers(citationService.getAllPapers());
  }, [researchResults]);

  // Update citation when selected paper or style changes
  useEffect(() => {
    if (selectedPaper) {
      const citation = citationService.formatCitation(selectedPaper, citationStyle);
      setFormattedCitation(citation);
    } else {
      setFormattedCitation('');
    }
  }, [selectedPaper, citationStyle]);

  // Update bibliography when papers or style changes
  useEffect(() => {
    if (papers.length > 0) {
      citationService.addPapers(papers);
      const formattedBibliography = citationService.exportBibliography(citationStyle, exportFormat);
      setBibliography(formattedBibliography);
    } else {
      setBibliography('');
    }
  }, [papers, citationStyle, exportFormat]);

  // Tab handling
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle paper selection
  const handleSelectPaper = (paper: CitationPaper) => {
    setSelectedPaper(paper);
  };

  // Handle citation style change
  const handleStyleChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setCitationStyle(event.target.value as CitationStyle);
  };

  // Handle export format change
  const handleExportFormatChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setExportFormat(event.target.value as 'txt' | 'html' | 'bibtex');
  };

  // Copy citation to clipboard
  const handleCopyCitation = () => {
    navigator.clipboard.writeText(formattedCitation);
    setSuccessMessage('Citation copied to clipboard');
  };

  // Copy bibliography to clipboard
  const handleCopyBibliography = () => {
    navigator.clipboard.writeText(bibliography);
    setSuccessMessage('Bibliography copied to clipboard');
  };

  // Download bibliography
  const handleDownloadBibliography = () => {
    const element = document.createElement('a');
    let fileContent = bibliography;
    let fileName = `bibliography.${exportFormat === 'bibtex' ? 'bib' : 'txt'}`;
    let mimeType = exportFormat === 'html' ? 'text/html' : 'text/plain';
    
    if (exportFormat === 'html') {
      fileContent = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Bibliography</title>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.5; margin: 2rem; }
    .bibliography p { margin-bottom: 1rem; }
  </style>
</head>
<body>
  <h1>Bibliography</h1>
  ${bibliography}
</body>
</html>`;
      fileName = 'bibliography.html';
    }
    
    const blob = new Blob([fileContent], { type: mimeType });
    element.href = URL.createObjectURL(blob);
    element.download = fileName;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    setSuccessMessage(`Bibliography downloaded as ${fileName}`);
  };

  // Delete a paper from the list
  const handleDeletePaper = (paperId: string) => {
    const updatedPapers = papers.filter(paper => paper.id !== paperId);
    setPapers(updatedPapers);
    
    if (selectedPaper && selectedPaper.id === paperId) {
      setSelectedPaper(null);
    }
    
    citationService.manager.removePaper(paperId);
    setSuccessMessage('Citation removed');
  };

  // Add paper dialog
  const handleOpenAddDialog = () => {
    setNewPaper({
      title: '',
      authors: [''],
      year: ''
    });
    setIsAddDialogOpen(true);
  };

  // Close add paper dialog
  const handleCloseAddDialog = () => {
    setIsAddDialogOpen(false);
  };

  // Handle author input changes
  const handleAuthorChange = (index: number, value: string) => {
    const updatedAuthors = [...(newPaper.authors || [''])];
    updatedAuthors[index] = value;
    setNewPaper({ ...newPaper, authors: updatedAuthors });
  };

  // Add an author field
  const handleAddAuthor = () => {
    setNewPaper({ ...newPaper, authors: [...(newPaper.authors || ['']), ''] });
  };

  // Remove an author field
  const handleRemoveAuthor = (index: number) => {
    const updatedAuthors = [...(newPaper.authors || [''])];
    updatedAuthors.splice(index, 1);
    if (updatedAuthors.length === 0) {
      updatedAuthors.push('');
    }
    setNewPaper({ ...newPaper, authors: updatedAuthors });
  };

  // Save a new paper
  const handleSavePaper = () => {
    if (!newPaper.title || !newPaper.authors || newPaper.authors.length === 0) {
      setError('Title and at least one author are required');
      return;
    }
    
    const paper: CitationPaper = {
      id: newPaper.id || `manual-${Date.now()}`,
      title: newPaper.title,
      authors: newPaper.authors.filter(author => author.trim() !== ''),
      year: newPaper.year,
      journal: newPaper.journal,
      conference: newPaper.conference,
      volume: newPaper.volume,
      issue: newPaper.issue,
      pages: newPaper.pages,
      publisher: newPaper.publisher,
      url: newPaper.url,
      doi: newPaper.doi,
      arxivId: newPaper.arxivId,
      abstract: includeAbstract ? newPaper.abstract : undefined
    };
    
    if (isEditDialogOpen) {
      // Update existing paper
      const updatedPapers = papers.map(p => p.id === paper.id ? paper : p);
      setPapers(updatedPapers);
      setSelectedPaper(paper);
      setIsEditDialogOpen(false);
    } else {
      // Add new paper
      setPapers([...papers, paper]);
      setSelectedPaper(paper);
      setIsAddDialogOpen(false);
    }
    
    // Add to citation service
    citationService.addPaper(paper);
    setSuccessMessage(isEditDialogOpen ? 'Citation updated' : 'Citation added');
  };

  // Edit a paper
  const handleEditPaper = (paper: CitationPaper) => {
    setNewPaper({
      ...paper,
      authors: [...paper.authors]
    });
    setIsEditDialogOpen(true);
  };

  // Close edit dialog
  const handleCloseEditDialog = () => {
    setIsEditDialogOpen(false);
  };

  // Open preferences dialog
  const handleOpenPreferencesDialog = () => {
    setIsPreferencesDialogOpen(true);
  };

  // Close preferences dialog
  const handleClosePreferencesDialog = () => {
    setIsPreferencesDialogOpen(false);
  };

  // Save preferences
  const handleSavePreferences = async () => {
    try {
      await citationService.savePreferences({
        defaultStyle: citationStyle,
        includeAbstract,
        defaultFormat: exportFormat
      });
      setSuccessMessage('Preferences saved');
    } catch (err) {
      console.error('Error saving preferences:', err);
      setError('Failed to save preferences');
    }
    setIsPreferencesDialogOpen(false);
  };

  // Open URL lookup dialog
  const handleOpenLookupDialog = () => {
    setLookupUrl('');
    setIsLookupDialogOpen(true);
  };

  // Close URL lookup dialog
  const handleCloseLookupDialog = () => {
    setIsLookupDialogOpen(false);
  };

  // Lookup a paper by URL/DOI/etc.
  const handleLookupPaper = async () => {
    if (!lookupUrl) {
      setError('Please enter a URL, DOI, or ArXiv ID');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const paper = await citationService.lookupUrl(lookupUrl);
      setPapers(prevPapers => {
        // Check if paper already exists
        const exists = prevPapers.some(p => p.id === paper.id);
        if (exists) {
          return prevPapers;
        }
        return [...prevPapers, paper];
      });
      setSelectedPaper(paper);
      setLookupUrl('');
      setIsLookupDialogOpen(false);
      setSuccessMessage('Citation added from lookup');
    } catch (err) {
      console.error('Error looking up paper:', err);
      setError('Failed to look up paper. Please check the URL or DOI and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Close error alert
  const handleCloseError = () => {
    setError(null);
  };

  // Close success alert
  const handleCloseSuccess = () => {
    setSuccessMessage(null);
  };

  // Use citation in parent component if provided
  const handleUseCitation = () => {
    if (onCite && selectedPaper) {
      onCite(formattedCitation, citationStyle);
      setSuccessMessage('Citation added to document');
    }
  };

  return (
    <Paper elevation={3} sx={{ mb: 3, overflow: 'hidden' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="citation manager tabs">
          <Tab label="Citations" id="citation-tab-0" aria-controls="citation-tabpanel-0" />
          <Tab label="Bibliography" id="citation-tab-1" aria-controls="citation-tabpanel-1" />
          <Tab label="Export" id="citation-tab-2" aria-controls="citation-tabpanel-2" />
        </Tabs>
      </Box>
      
      <TabPanel value={tabValue} index={0}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6">Cited Papers</Typography>
          <Box>
            <Button 
              variant="outlined" 
              startIcon={<AddIcon />} 
              onClick={handleOpenAddDialog}
              sx={{ mr: 1 }}
            >
              Add Manual
            </Button>
            <Button 
              variant="outlined" 
              startIcon={<FileCopyIcon />} 
              onClick={handleOpenLookupDialog}
            >
              Lookup
            </Button>
          </Box>
        </Box>
        
        {error && (
          <Alert 
            severity="error" 
            onClose={handleCloseError}
            sx={{ mb: 2 }}
          >
            {error}
          </Alert>
        )}
        
        <Box sx={{ display: 'flex', height: '300px' }}>
          <Paper 
            variant="outlined" 
            sx={{ 
              width: '40%', 
              mr: 2, 
              overflowY: 'auto', 
              p: 1
            }}
          >
            {papers.length === 0 ? (
              <Typography variant="body2" color="textSecondary" sx={{ p: 2, textAlign: 'center' }}>
                No papers cited yet. Add a paper manually or import from search results.
              </Typography>
            ) : (
              <List>
                {papers.map((paper) => (
                  <ListItem
                    key={paper.id}
                    button
                    selected={selectedPaper?.id === paper.id}
                    onClick={() => handleSelectPaper(paper)}
                    secondaryAction={
                      <Box>
                        <IconButton 
                          edge="end" 
                          aria-label="edit" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleEditPaper(paper);
                          }}
                          size="small"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                        <IconButton 
                          edge="end" 
                          aria-label="delete" 
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeletePaper(paper.id);
                          }}
                          size="small"
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Box>
                    }
                  >
                    <ListItemText
                      primary={paper.title}
                      secondary={
                        <>
                          <Typography variant="body2" component="span">
                            {paper.authors.join(', ')}
                            {paper.year ? ` (${paper.year})` : ''}
                          </Typography>
                          <Box mt={0.5}>
                            {paper.journal && (
                              <Chip 
                                label={paper.journal} 
                                size="small" 
                                sx={{ mr: 0.5, mb: 0.5 }} 
                                variant="outlined" 
                              />
                            )}
                            {paper.conference && (
                              <Chip 
                                label={paper.conference} 
                                size="small" 
                                sx={{ mr: 0.5, mb: 0.5 }} 
                                variant="outlined" 
                              />
                            )}
                            {paper.doi && (
                              <Chip 
                                label="DOI" 
                                size="small" 
                                sx={{ mr: 0.5, mb: 0.5 }} 
                                color="primary" 
                                variant="outlined" 
                              />
                            )}
                            {paper.arxivId && (
                              <Chip 
                                label="arXiv" 
                                size="small" 
                                sx={{ mr: 0.5, mb: 0.5 }} 
                                color="secondary" 
                                variant="outlined" 
                              />
                            )}
                          </Box>
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
          
          <Paper 
            variant="outlined" 
            sx={{ 
              width: '60%', 
              p: 2,
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <FormControl variant="outlined" size="small" sx={{ width: 200 }}>
                <InputLabel id="citation-style-label">Citation Style</InputLabel>
                <Select
                  labelId="citation-style-label"
                  value={citationStyle}
                  onChange={handleStyleChange}
                  label="Citation Style"
                >
                  {citationService.getSupportedStyles().map((style) => (
                    <MenuItem key={style} value={style}>{style}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              {onCite && (
                <Button
                  variant="contained"
                  onClick={handleUseCitation}
                  disabled={!selectedPaper}
                >
                  Use Citation
                </Button>
              )}
            </Box>
            
            {selectedPaper ? (
              <>
                <Typography variant="subtitle2" gutterBottom>Formatted Citation:</Typography>
                <Paper 
                  variant="outlined"
                  sx={{ 
                    p: 2, 
                    mb: 2,
                    flexGrow: 1,
                    position: 'relative',
                    overflow: 'auto'
                  }}
                >
                  <Typography variant="body2">{formattedCitation}</Typography>
                  <IconButton
                    size="small"
                    onClick={handleCopyCitation}
                    sx={{ 
                      position: 'absolute',
                      right: 8,
                      top: 8
                    }}
                  >
                    <ContentCopyIcon fontSize="small" />
                  </IconButton>
                </Paper>
                
                <Typography variant="subtitle2" gutterBottom>Paper Details:</Typography>
                <Box sx={{ overflow: 'auto' }}>
                  <List dense>
                    <ListItem>
                      <ListItemText primary="Title" secondary={selectedPaper.title} />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="Authors" secondary={selectedPaper.authors.join(', ')} />
                    </ListItem>
                    {selectedPaper.year && (
                      <ListItem>
                        <ListItemText primary="Year" secondary={selectedPaper.year} />
                      </ListItem>
                    )}
                    {selectedPaper.journal && (
                      <ListItem>
                        <ListItemText primary="Journal" secondary={selectedPaper.journal} />
                      </ListItem>
                    )}
                    {selectedPaper.conference && (
                      <ListItem>
                        <ListItemText primary="Conference" secondary={selectedPaper.conference} />
                      </ListItem>
                    )}
                    {selectedPaper.doi && (
                      <ListItem>
                        <ListItemText 
                          primary="DOI" 
                          secondary={
                            <a 
                              href={`https://doi.org/${selectedPaper.doi}`} 
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              {selectedPaper.doi}
                            </a>
                          } 
                        />
                      </ListItem>
                    )}
                    {selectedPaper.url && (
                      <ListItem>
                        <ListItemText 
                          primary="URL" 
                          secondary={
                            <a 
                              href={selectedPaper.url} 
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              {selectedPaper.url}
                            </a>
                          } 
                        />
                      </ListItem>
                    )}
                  </List>
                </Box>
              </>
            ) : (
              <Box 
                sx={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  height: '100%'
                }}
              >
                <Typography variant="body1" color="textSecondary">
                  Select a paper to view and copy its citation.
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
      </TabPanel>
      
      <TabPanel value={tabValue} index={1}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6">Bibliography</Typography>
          <Box>
            <FormControl variant="outlined" size="small" sx={{ width: 150, mr: 1 }}>
              <InputLabel id="bibliography-style-label">Citation Style</InputLabel>
              <Select
                labelId="bibliography-style-label"
                value={citationStyle}
                onChange={handleStyleChange}
                label="Citation Style"
              >
                {citationService.getSupportedStyles().map((style) => (
                  <MenuItem key={style} value={style}>{style}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button 
              variant="outlined" 
              startIcon={<ContentCopyIcon />} 
              onClick={handleCopyBibliography}
              disabled={papers.length === 0}
            >
              Copy All
            </Button>
          </Box>
        </Box>
        
        {papers.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <Typography variant="body1" color="textSecondary">
              No papers cited yet. Add papers in the Citations tab to generate a bibliography.
            </Typography>
          </Box>
        ) : (
          <Paper 
            variant="outlined" 
            sx={{ 
              p: 2,
              maxHeight: '300px',
              overflow: 'auto',
              position: 'relative',
              fontFamily: citationStyle === 'BibTeX' ? '"Courier New", monospace' : 'inherit'
            }}
          >
            <Typography
              variant="body2"
              component="div"
              sx={{
                whiteSpace: citationStyle === 'BibTeX' ? 'pre-wrap' : 'normal',
                '& > p': {
                  marginBottom: '1rem'
                }
              }}
            >
              {citationStyle === 'BibTeX' ? (
                <pre style={{ margin: 0 }}>{bibliography}</pre>
              ) : (
                bibliography.split('\n\n').map((citation, index) => (
                  <p key={index}>{citation}</p>
                ))
              )}
            </Typography>
          </Paper>
        )}
      </TabPanel>
      
      <TabPanel value={tabValue} index={2}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6">Export Bibliography</Typography>
          <Button 
            variant="outlined" 
            startIcon={<DownloadIcon />} 
            onClick={handleDownloadBibliography}
            disabled={papers.length === 0}
          >
            Download
          </Button>
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Format Options</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <FormControl variant="outlined" size="small" sx={{ width: 150, mr: 2 }}>
              <InputLabel id="export-format-label">Export Format</InputLabel>
              <Select
                labelId="export-format-label"
                value={exportFormat}
                onChange={handleExportFormatChange}
                label="Export Format"
              >
                <MenuItem value="txt">Plain Text</MenuItem>
                <MenuItem value="html">HTML</MenuItem>
                <MenuItem value="bibtex">BibTeX</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl variant="outlined" size="small" sx={{ width: 150, mr: 2 }}>
              <InputLabel id="export-style-label">Citation Style</InputLabel>
              <Select
                labelId="export-style-label"
                value={exportFormat === 'bibtex' ? 'BibTeX' : citationStyle}
                onChange={handleStyleChange}
                label="Citation Style"
                disabled={exportFormat === 'bibtex'}
              >
                {citationService.getSupportedStyles().map((style) => (
                  <MenuItem key={style} value={style}>{style}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <Button
              variant="outlined"
              onClick={handleOpenPreferencesDialog}
              size="small"
            >
              Preferences
            </Button>
          </Box>
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Preview</Typography>
          {papers.length === 0 ? (
            <Typography variant="body2" color="textSecondary">
              No papers cited yet. Add papers in the Citations tab to generate export preview.
            </Typography>
          ) : (
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 2,
                maxHeight: '200px',
                overflow: 'auto',
                position: 'relative',
                fontFamily: exportFormat === 'bibtex' || citationStyle === 'BibTeX' ? '"Courier New", monospace' : 'inherit'
              }}
            >
              <Typography
                variant="body2"
                component="div"
                sx={{
                  whiteSpace: exportFormat === 'bibtex' || citationStyle === 'BibTeX' ? 'pre-wrap' : 'normal'
                }}
              >
                {exportFormat === 'bibtex' || citationStyle === 'BibTeX' ? (
                  <pre style={{ margin: 0 }}>{bibliography}</pre>
                ) : exportFormat === 'html' ? (
                  <div dangerouslySetInnerHTML={{ __html: bibliography }} />
                ) : (
                  bibliography.split('\n\n').map((citation, index) => (
                    <p key={index}>{citation}</p>
                  ))
                )}
              </Typography>
            </Paper>
          )}
        </Box>
        
        <Alert severity="info">
          <Typography variant="body2">
            Export your bibliography in various formats for use in papers, reports, or reference managers.
            The BibTeX format is widely supported by reference managers like Zotero, Mendeley, and EndNote.
          </Typography>
        </Alert>
      </TabPanel>
      
      {/* Add Paper Dialog */}
      <Dialog open={isAddDialogOpen} onClose={handleCloseAddDialog} maxWidth="md" fullWidth>
        <DialogTitle>Add Citation Manually</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={newPaper.title || ''}
              onChange={(e) => setNewPaper({ ...newPaper, title: e.target.value })}
              required
            />
            
            <Typography variant="subtitle2">Authors</Typography>
            {newPaper.authors?.map((author, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <TextField
                  label={`Author ${index + 1}`}
                  fullWidth
                  value={author}
                  onChange={(e) => handleAuthorChange(index, e.target.value)}
                  required={index === 0}
                />
                {index > 0 && (
                  <IconButton onClick={() => handleRemoveAuthor(index)} size="small">
                    <DeleteIcon />
                  </IconButton>
                )}
              </Box>
            ))}
            <Button 
              variant="outlined" 
              startIcon={<AddIcon />} 
              onClick={handleAddAuthor}
              sx={{ alignSelf: 'flex-start' }}
            >
              Add Author
            </Button>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Year"
                value={newPaper.year || ''}
                onChange={(e) => setNewPaper({ ...newPaper, year: e.target.value })}
                sx={{ width: '30%' }}
              />
              <TextField
                label="Journal"
                value={newPaper.journal || ''}
                onChange={(e) => setNewPaper({ ...newPaper, journal: e.target.value })}
                sx={{ width: '70%' }}
              />
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Conference"
                value={newPaper.conference || ''}
                onChange={(e) => setNewPaper({ ...newPaper, conference: e.target.value })}
                fullWidth
              />
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Volume"
                value={newPaper.volume || ''}
                onChange={(e) => setNewPaper({ ...newPaper, volume: e.target.value })}
                sx={{ width: '30%' }}
              />
              <TextField
                label="Issue"
                value={newPaper.issue || ''}
                onChange={(e) => setNewPaper({ ...newPaper, issue: e.target.value })}
                sx={{ width: '30%' }}
              />
              <TextField
                label="Pages"
                value={newPaper.pages || ''}
                onChange={(e) => setNewPaper({ ...newPaper, pages: e.target.value })}
                sx={{ width: '40%' }}
                placeholder="e.g., 123-145"
              />
            </Box>
            
            <TextField
              label="DOI"
              value={newPaper.doi || ''}
              onChange={(e) => setNewPaper({ ...newPaper, doi: e.target.value })}
              placeholder="e.g., 10.1000/xyz123"
            />
            
            <TextField
              label="URL"
              value={newPaper.url || ''}
              onChange={(e) => setNewPaper({ ...newPaper, url: e.target.value })}
              placeholder="e.g., https://example.com/paper"
            />
            
            <Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={includeAbstract}
                    onChange={(e) => setIncludeAbstract(e.target.checked)}
                  />
                }
                label="Include Abstract"
              />
            </Box>
            
            {includeAbstract && (
              <TextField
                label="Abstract"
                multiline
                rows={4}
                value={newPaper.abstract || ''}
                onChange={(e) => setNewPaper({ ...newPaper, abstract: e.target.value })}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAddDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSavePaper} color="primary" variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Edit Paper Dialog - shares same form as Add Paper Dialog */}
      <Dialog open={isEditDialogOpen} onClose={handleCloseEditDialog} maxWidth="md" fullWidth>
        <DialogTitle>Edit Citation</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              label="Title"
              fullWidth
              value={newPaper.title || ''}
              onChange={(e) => setNewPaper({ ...newPaper, title: e.target.value })}
              required
            />
            
            <Typography variant="subtitle2">Authors</Typography>
            {newPaper.authors?.map((author, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <TextField
                  label={`Author ${index + 1}`}
                  fullWidth
                  value={author}
                  onChange={(e) => handleAuthorChange(index, e.target.value)}
                  required={index === 0}
                />
                {index > 0 && (
                  <IconButton onClick={() => handleRemoveAuthor(index)} size="small">
                    <DeleteIcon />
                  </IconButton>
                )}
              </Box>
            ))}
            <Button 
              variant="outlined" 
              startIcon={<AddIcon />} 
              onClick={handleAddAuthor}
              sx={{ alignSelf: 'flex-start' }}
            >
              Add Author
            </Button>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Year"
                value={newPaper.year || ''}
                onChange={(e) => setNewPaper({ ...newPaper, year: e.target.value })}
                sx={{ width: '30%' }}
              />
              <TextField
                label="Journal"
                value={newPaper.journal || ''}
                onChange={(e) => setNewPaper({ ...newPaper, journal: e.target.value })}
                sx={{ width: '70%' }}
              />
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Conference"
                value={newPaper.conference || ''}
                onChange={(e) => setNewPaper({ ...newPaper, conference: e.target.value })}
                fullWidth
              />
            </Box>
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Volume"
                value={newPaper.volume || ''}
                onChange={(e) => setNewPaper({ ...newPaper, volume: e.target.value })}
                sx={{ width: '30%' }}
              />
              <TextField
                label="Issue"
                value={newPaper.issue || ''}
                onChange={(e) => setNewPaper({ ...newPaper, issue: e.target.value })}
                sx={{ width: '30%' }}
              />
              <TextField
                label="Pages"
                value={newPaper.pages || ''}
                onChange={(e) => setNewPaper({ ...newPaper, pages: e.target.value })}
                sx={{ width: '40%' }}
                placeholder="e.g., 123-145"
              />
            </Box>
            
            <TextField
              label="DOI"
              value={newPaper.doi || ''}
              onChange={(e) => setNewPaper({ ...newPaper, doi: e.target.value })}
              placeholder="e.g., 10.1000/xyz123"
            />
            
            <TextField
              label="URL"
              value={newPaper.url || ''}
              onChange={(e) => setNewPaper({ ...newPaper, url: e.target.value })}
              placeholder="e.g., https://example.com/paper"
            />
            
            <Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={includeAbstract}
                    onChange={(e) => setIncludeAbstract(e.target.checked)}
                  />
                }
                label="Include Abstract"
              />
            </Box>
            
            {includeAbstract && (
              <TextField
                label="Abstract"
                multiline
                rows={4}
                value={newPaper.abstract || ''}
                onChange={(e) => setNewPaper({ ...newPaper, abstract: e.target.value })}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSavePaper} color="primary" variant="contained">
            Update
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Preferences Dialog */}
      <Dialog open={isPreferencesDialogOpen} onClose={handleClosePreferencesDialog}>
        <DialogTitle>Citation Preferences</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1, minWidth: '300px' }}>
            <FormControl fullWidth>
              <InputLabel id="default-style-label">Default Citation Style</InputLabel>
              <Select
                labelId="default-style-label"
                value={citationStyle}
                onChange={handleStyleChange}
                label="Default Citation Style"
              >
                {citationService.getSupportedStyles().map((style) => (
                  <MenuItem key={style} value={style}>{style}</MenuItem>
                ))}
              </Select>
            </FormControl>
            
            <FormControl fullWidth>
              <InputLabel id="default-format-label">Default Export Format</InputLabel>
              <Select
                labelId="default-format-label"
                value={exportFormat}
                onChange={handleExportFormatChange}
                label="Default Export Format"
              >
                <MenuItem value="txt">Plain Text</MenuItem>
                <MenuItem value="html">HTML</MenuItem>
                <MenuItem value="bibtex">BibTeX</MenuItem>
              </Select>
            </FormControl>
            
            <FormControlLabel
              control={
                <Switch
                  checked={includeAbstract}
                  onChange={(e) => setIncludeAbstract(e.target.checked)}
                />
              }
              label="Include Abstracts When Available"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClosePreferencesDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSavePreferences} color="primary" variant="contained">
            Save Preferences
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Lookup URL Dialog */}
      <Dialog open={isLookupDialogOpen} onClose={handleCloseLookupDialog}>
        <DialogTitle>Look Up Citation</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1, minWidth: '400px' }}>
            <Typography variant="body2" gutterBottom>
              Enter a URL, DOI, or ArXiv ID to look up a citation.
            </Typography>
            
            <TextField
              label="URL, DOI, or ArXiv ID"
              fullWidth
              value={lookupUrl}
              onChange={(e) => setLookupUrl(e.target.value)}
              placeholder="e.g., https://doi.org/10.1000/xyz123 or 10.1000/xyz123"
              disabled={loading}
              error={!!error}
              helperText={error || ''}
            />
            
            <Alert severity="info">
              <Typography variant="caption">
                Supported formats:
                <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                  <li>DOI: 10.1000/xyz123</li>
                  <li>ArXiv URL: https://arxiv.org/abs/2101.12345</li>
                  <li>DOI URL: https://doi.org/10.1000/xyz123</li>
                </ul>
              </Typography>
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseLookupDialog} color="primary" disabled={loading}>
            Cancel
          </Button>
          <Button 
            onClick={handleLookupPaper} 
            color="primary" 
            variant="contained"
            disabled={!lookupUrl.trim() || loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Look Up'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Success message */}
      <Snackbar
        open={!!successMessage}
        autoHideDuration={3000}
        onClose={handleCloseSuccess}
        message={successMessage}
        action={
          <IconButton
            size="small"
            aria-label="close"
            color="inherit"
            onClick={handleCloseSuccess}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        }
      />
    </Paper>
  );
};

export default CitationManager;
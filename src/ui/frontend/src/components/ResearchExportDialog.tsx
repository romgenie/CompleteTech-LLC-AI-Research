import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Checkbox,
  FormGroup,
  Typography,
  Box,
  Divider
} from '@mui/material';
import { ExportFormat, ExportOptions } from '../types/research';

interface ResearchExportDialogProps {
  open: boolean;
  onClose: () => void;
  onExport: (options: ExportOptions) => void;
}

/**
 * Dialog for configuring research export options
 */
const ResearchExportDialog: React.FC<ResearchExportDialogProps> = ({
  open,
  onClose,
  onExport
}) => {
  const [format, setFormat] = useState<ExportFormat>('pdf');
  const [includeSources, setIncludeSources] = useState(true);
  const [includeGraphVisual, setIncludeGraphVisual] = useState(true);
  const [includeTags, setIncludeTags] = useState(true);
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [citationStyle, setCitationStyle] = useState('apa');
  const [includeReferences, setIncludeReferences] = useState(true);

  const handleExport = () => {
    onExport({
      format,
      includeSources,
      includeGraphVisual,
      includeTags,
      includeMetadata,
      citations: {
        style: citationStyle,
        includeReferences
      }
    });
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
      fullWidth
    >
      <DialogTitle>Export Research</DialogTitle>
      <DialogContent>
        <Box my={2}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="export-format-label">Format</InputLabel>
            <Select
              labelId="export-format-label"
              value={format}
              label="Format"
              onChange={(e) => setFormat(e.target.value as ExportFormat)}
            >
              <MenuItem value="pdf">PDF Document</MenuItem>
              <MenuItem value="markdown">Markdown</MenuItem>
              <MenuItem value="html">HTML</MenuItem>
              <MenuItem value="docx">Word Document (DOCX)</MenuItem>
              <MenuItem value="text">Plain Text</MenuItem>
            </Select>
          </FormControl>
        </Box>

        <Typography variant="subtitle2" gutterBottom>Content Options</Typography>
        <FormGroup>
          <FormControlLabel 
            control={
              <Checkbox 
                checked={includeSources} 
                onChange={(e) => setIncludeSources(e.target.checked)} 
              />
            } 
            label="Include sources" 
          />
          <FormControlLabel 
            control={
              <Checkbox 
                checked={includeGraphVisual} 
                onChange={(e) => setIncludeGraphVisual(e.target.checked)} 
              />
            } 
            label="Include knowledge graph visualization" 
          />
          <FormControlLabel 
            control={
              <Checkbox 
                checked={includeTags} 
                onChange={(e) => setIncludeTags(e.target.checked)} 
              />
            } 
            label="Include tags" 
          />
          <FormControlLabel 
            control={
              <Checkbox 
                checked={includeMetadata} 
                onChange={(e) => setIncludeMetadata(e.target.checked)} 
              />
            } 
            label="Include metadata" 
          />
        </FormGroup>

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" gutterBottom>Citation Options</Typography>
        <FormControl fullWidth margin="normal">
          <InputLabel id="citation-style-label">Citation Style</InputLabel>
          <Select
            labelId="citation-style-label"
            value={citationStyle}
            label="Citation Style"
            onChange={(e) => setCitationStyle(e.target.value)}
          >
            <MenuItem value="apa">APA</MenuItem>
            <MenuItem value="mla">MLA</MenuItem>
            <MenuItem value="chicago">Chicago</MenuItem>
            <MenuItem value="harvard">Harvard</MenuItem>
            <MenuItem value="ieee">IEEE</MenuItem>
            <MenuItem value="vancouver">Vancouver</MenuItem>
            <MenuItem value="nature">Nature</MenuItem>
          </Select>
        </FormControl>
        <FormGroup>
          <FormControlLabel 
            control={
              <Checkbox 
                checked={includeReferences} 
                onChange={(e) => setIncludeReferences(e.target.checked)} 
              />
            } 
            label="Include references section" 
          />
        </FormGroup>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleExport} variant="contained" color="primary">
          Export
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ResearchExportDialog;
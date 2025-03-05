import React from 'react';
import { Box, Button, IconButton, Select, MenuItem, Typography, useTheme } from '@mui/material';
import { 
  FirstPage, 
  LastPage, 
  NavigateNext, 
  NavigateBefore,
  KeyboardArrowLeft,
  KeyboardArrowRight
} from '@mui/icons-material';

/**
 * Pagination component for displaying pagination controls
 * 
 * @param {Object} props - Component props
 * @param {number} props.page - Current page number (1-indexed)
 * @param {number} props.pageSize - Number of items per page
 * @param {number} props.total - Total number of items
 * @param {number} props.totalPages - Total number of pages
 * @param {Function} props.onPageChange - Callback when page changes
 * @param {Function} props.onPageSizeChange - Callback when page size changes
 * @param {boolean} props.loading - Whether data is currently loading
 * @param {boolean} props.hidePageSizeSelector - Whether to hide the page size selector
 * @param {Array<number>} props.pageSizeOptions - Available page size options
 * @param {boolean} props.showFirstLastButtons - Whether to show first/last page buttons
 * @param {boolean} props.compact - Whether to use compact layout
 * @param {number} props.siblingCount - Number of sibling pages to show
 * @returns {JSX.Element} Pagination component
 */
function Pagination({
  page = 1,
  pageSize = 10,
  total = 0,
  totalPages,
  onPageChange,
  onPageSizeChange,
  loading = false,
  hidePageSizeSelector = false,
  pageSizeOptions = [5, 10, 25, 50, 100],
  showFirstLastButtons = true,
  compact = false,
  siblingCount = 1
}) {
  const theme = useTheme();

  // Calculate total pages if not provided
  const calculatedTotalPages = totalPages || Math.ceil(total / pageSize) || 1;
  
  // Function to handle page change
  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= calculatedTotalPages && !loading) {
      onPageChange(newPage);
    }
  };

  // Function to handle page size change
  const handlePageSizeChange = (event) => {
    if (!loading) {
      onPageSizeChange(Number(event.target.value));
    }
  };

  // Create page range for pagination buttons
  const getPageRange = () => {
    const range = [];
    const totalPageButtons = siblingCount * 2 + 1; // siblings on both sides + current page
    
    // If total pages is less than or equal to total buttons, show all pages
    if (calculatedTotalPages <= totalPageButtons) {
      for (let i = 1; i <= calculatedTotalPages; i++) {
        range.push(i);
      }
      return range;
    }
    
    // Calculate start and end of range with current page in the middle
    let start = Math.max(1, page - siblingCount);
    let end = Math.min(calculatedTotalPages, page + siblingCount);
    
    // Adjust start and end if we're at the beginning or end
    if (page <= siblingCount) {
      end = totalPageButtons;
    } else if (page > calculatedTotalPages - siblingCount) {
      start = calculatedTotalPages - totalPageButtons + 1;
    }
    
    // Create range array
    for (let i = start; i <= end; i++) {
      range.push(i);
    }
    
    // Add ellipsis at the beginning if needed
    if (start > 1) {
      range.unshift('...');
      range.unshift(1);
    }
    
    // Add ellipsis at the end if needed
    if (end < calculatedTotalPages) {
      range.push('...');
      range.push(calculatedTotalPages);
    }
    
    return range;
  };

  // Create the page range
  const pageRange = getPageRange();

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 1,
        mt: 2,
        mb: 2,
        py: 1,
        ...(compact ? { px: 1 } : { px: 2 }),
        borderRadius: 1,
        backgroundColor: theme.palette.background.paper,
        boxShadow: theme.shadows[1],
      }}
    >
      {/* Page size selector */}
      {!hidePageSizeSelector && (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Rows per page:
          </Typography>
          <Select
            value={pageSize}
            onChange={handlePageSizeChange}
            size="small"
            sx={{ minWidth: 80 }}
            disabled={loading}
          >
            {pageSizeOptions.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </Select>
        </Box>
      )}

      {/* Pagination controls */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {/* First page button */}
        {showFirstLastButtons && (
          <IconButton
            onClick={() => handlePageChange(1)}
            disabled={page === 1 || loading}
            size="small"
          >
            <FirstPage fontSize="small" />
          </IconButton>
        )}

        {/* Previous page button */}
        <IconButton
          onClick={() => handlePageChange(page - 1)}
          disabled={page === 1 || loading}
          size="small"
        >
          <NavigateBefore fontSize="small" />
        </IconButton>

        {/* Page buttons */}
        {!compact && pageRange.map((pageNum, index) => (
          pageNum === '...' ? (
            <Typography
              key={`ellipsis-${index}`}
              variant="body2"
              sx={{ mx: 1 }}
            >
              ...
            </Typography>
          ) : (
            <Button
              key={pageNum}
              variant={pageNum === page ? "contained" : "outlined"}
              onClick={() => handlePageChange(pageNum)}
              disabled={loading}
              size="small"
              sx={{
                minWidth: 36,
                height: 36,
                p: 0,
                mx: 0.25
              }}
            >
              {pageNum}
            </Button>
          )
        ))}

        {/* Compact page indicator */}
        {compact && (
          <Typography variant="body2" sx={{ mx: 1 }}>
            Page {page} of {calculatedTotalPages}
          </Typography>
        )}

        {/* Next page button */}
        <IconButton
          onClick={() => handlePageChange(page + 1)}
          disabled={page === calculatedTotalPages || loading}
          size="small"
        >
          <NavigateNext fontSize="small" />
        </IconButton>

        {/* Last page button */}
        {showFirstLastButtons && (
          <IconButton
            onClick={() => handlePageChange(calculatedTotalPages)}
            disabled={page === calculatedTotalPages || loading}
            size="small"
          >
            <LastPage fontSize="small" />
          </IconButton>
        )}
      </Box>

      {/* Page info */}
      <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
        <Typography variant="body2" color="text.secondary">
          {loading ? 'Loading...' : `Showing ${Math.min((page - 1) * pageSize + 1, total)} - ${Math.min(page * pageSize, total)} of ${total} items`}
        </Typography>
      </Box>
    </Box>
  );
}

export default Pagination;
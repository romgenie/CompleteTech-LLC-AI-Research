import React, { useState } from 'react';
import { useNavigate, useLocation, Location } from 'react-router-dom';
import {
  Avatar,
  Button,
  TextField,
  Paper,
  Box,
  Grid,
  Typography,
  Container,
  Alert,
  Snackbar,
} from '@mui/material';
import { LockOutlined as LockOutlinedIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

// Custom type for location state with "from" property
interface LocationWithState extends Location {
  state?: {
    from?: string;
  };
}

/**
 * Login page component.
 * 
 * @returns {React.ReactElement} Login page
 */
function Login(): JSX.Element {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation() as LocationWithState;

  // Get redirect path from location state
  const from = location.state?.from || '/';

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    
    // Validate form
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password');
      return;
    }
    
    try {
      setError('');
      setLoading(true);
      
      await login(username, password);
      
      // Navigate to the page user was trying to access or dashboard
      navigate(from, { replace: true });
    } catch (err) {
      console.error('Login error:', err);
      setError(err instanceof Error ? err.message : 'Failed to login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        width: '100%',
        padding: { xs: 2, sm: 4 },
        backgroundColor: theme => theme.palette.grey[100]
      }}
    >
      <Grid container spacing={0} sx={{ 
        maxWidth: '1200px', 
        borderRadius: '8px',
        overflow: 'hidden',
        boxShadow: 8,
        width: '100%',
        margin: 0
      }}>
          <Grid
            item
            xs={false}
            sm={6}
            md={7}
            sx={{
              backgroundImage: 'url(https://source.unsplash.com/random?ai,research)',
              backgroundRepeat: 'no-repeat',
              backgroundColor: (t) =>
                t.palette.mode === 'light' ? t.palette.grey[50] : t.palette.grey[900],
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              minHeight: { xs: '0', sm: '500px' },
              display: { xs: 'none', sm: 'block' }
            }}
          />
          <Grid 
            item 
            xs={12} 
            sm={6} 
            md={5} 
            component={Paper} 
            elevation={6} 
            square 
            sx={{ 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: { xs: 2, sm: 4 }
            }}
          >
            <Box
              sx={{
                width: '100%',
                maxWidth: '400px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
              }}
            >
              <Avatar sx={{ width: 56, height: 56, mb: 2, bgcolor: 'secondary.main' }}>
                <LockOutlinedIcon />
              </Avatar>
              <Typography component="h1" variant="h4" gutterBottom>
                AI Research Integration
              </Typography>
              <Typography variant="subtitle1" color="text.secondary" align="center" sx={{ mb: 3 }}>
                Sign in to access the platform
              </Typography>
              <Box component="form" noValidate onSubmit={handleSubmit} sx={{ width: '100%' }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="username"
                  label="Username"
                  name="username"
                  autoComplete="username"
                  autoFocus
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={loading}
                  variant="outlined"
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="password"
                  label="Password"
                  type="password"
                  id="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  variant="outlined"
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  sx={{ mt: 3, mb: 2, py: 1.5 }}
                  disabled={loading}
                >
                  {loading ? 'Signing In...' : 'Sign In'}
                </Button>
                
                <Box sx={{ 
                  mt: 3, 
                  p: 2, 
                  bgcolor: 'action.hover', 
                  borderRadius: 1,
                  textAlign: 'center'
                }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Demo Credentials</strong>
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Username: <strong>admin</strong> | Password: <strong>password</strong>
                  </Typography>
                </Box>
              </Box>
            </Box>
          </Grid>
        </Grid>
      {/* Error Snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setError('')} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default Login;
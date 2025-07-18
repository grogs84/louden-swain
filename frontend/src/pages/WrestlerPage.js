import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Chip,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
} from '@mui/material';
import { wrestlersAPI } from '../services/api';
import { formatFullName, formatSchoolName, formatLocation } from '../utils/formatters';

const WrestlerPage = () => {
  const { id } = useParams();

  const { data: wrestler, isLoading, error } = useQuery(
    ['wrestler', id],
    () => wrestlersAPI.getById(id).then(res => res.data),
    { enabled: !!id }
  );

  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery(
    ['wrestler-stats', id, 'v2'], // Added version to force cache refresh
    () => wrestlersAPI.getStats(id).then(res => {
      // console.log('Stats API response:', res.data);
      return res.data;
    }),
    { 
      enabled: !!id,
      staleTime: 0, // Don't cache
      cacheTime: 0  // Don't cache
    }
  );

  const { data: matches, isLoading: matchesLoading, error: matchesError } = useQuery(
    ['wrestler-matches', id],
    () => wrestlersAPI.getMatches(id, { limit: 10 }).then(res => res.data),
    { enabled: !!id }
  );

  // console.log('Stats data:', stats, 'Loading:', statsLoading, 'Error:', statsError);

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Error loading wrestler data: {error.message}
      </Alert>
    );
  }

  if (!wrestler) {
    return <Alert severity="info">Wrestler not found</Alert>;
  }

  return (
    <Container maxWidth="lg">
      {/* Header */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h3" component="h1" gutterBottom>
              {formatFullName(wrestler.first_name, wrestler.last_name)}
            </Typography>
            <Typography variant="h5" color="text.secondary" gutterBottom>
              {formatSchoolName(wrestler.school?.name)}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
              {/* <Chip label={`${wrestler.weight_class} lbs`} color="primary" /> */}
              {/* <Chip label={wrestler.year || 'Senior'} variant="outlined" /> */}
              {wrestler.hometown && wrestler.state && (
                <Chip label={formatLocation(`${wrestler.hometown}, ${wrestler.state}`)} variant="outlined" />
              )}
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: { xs: 'left', md: 'right' } }}>
              {wrestler.height && (
                <Typography variant="body1">
                  <strong>Height:</strong> {wrestler.height}
                </Typography>
              )}
              {wrestler.weight && (
                <Typography variant="body1">
                  <strong>Weight:</strong> {wrestler.weight} lbs
                </Typography>
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={4}>
        {/* Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Season Statistics
              </Typography>
              {stats ? (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="h6" color="primary">
                      {stats.wins}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Wins
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6" color="error">
                      {stats.losses}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Losses
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6">
                      {stats.win_percentage.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Win Rate
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6">
                      {stats.pins}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Pins
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6">
                      {stats.tech_falls}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Tech Falls
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6">
                      {stats.major_decisions}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Major Decisions
                    </Typography>
                  </Grid>
                </Grid>
              ) : statsLoading ? (
                <Typography color="text.secondary">
                  Loading statistics...
                </Typography>
              ) : statsError ? (
                <Typography color="error">
                  Error loading statistics: {statsError.message}
                </Typography>
              ) : (
                <Typography color="text.secondary">
                  Statistics not available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Facts */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Quick Facts
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>School:</strong> {formatSchoolName(wrestler.school?.name)}
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Conference:</strong> {wrestler.school?.conference || 'N/A'}
              </Typography>
              {wrestler.hometown && wrestler.state && (
                <Typography variant="body1" paragraph>
                  <strong>Hometown:</strong> {formatLocation(`${wrestler.hometown}, ${wrestler.state}`)}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Match History */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Recent Matches
              </Typography>
              {matches && matches.length > 0 ? (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Year</TableCell>
                        <TableCell>Weight</TableCell>
                        <TableCell>Opponent</TableCell>
                        <TableCell>Result</TableCell>
                        <TableCell>Score</TableCell>
                        <TableCell>Round</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {matches.map((match) => (
                        <TableRow key={match.id}>
                          <TableCell>{match.year}</TableCell>
                          <TableCell>{match.weight_class} lbs</TableCell>
                          <TableCell>{formatFullName(match.opponent_first_name || '', match.opponent_last_name || match.opponent || '')}</TableCell>
                          <TableCell>
                            <Chip
                              label={match.result}
                              color={match.result === 'W' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{match.score}</TableCell>
                          <TableCell>{match.round}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : matchesLoading ? (
                <Typography color="text.secondary">
                  Loading matches...
                </Typography>
              ) : matchesError ? (
                <Typography color="error">
                  Error loading matches: {matchesError.message}
                </Typography>
              ) : (
                <Typography color="text.secondary">
                  No match history available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default WrestlerPage;

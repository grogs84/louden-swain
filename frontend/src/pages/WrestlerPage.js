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

const WrestlerPage = () => {
  const { id } = useParams();

  const { data: wrestler, isLoading, error } = useQuery(
    ['wrestler', id],
    () => wrestlersAPI.getById(id).then(res => res.data),
    { enabled: !!id }
  );

  const { data: stats } = useQuery(
    ['wrestler-stats', id],
    () => wrestlersAPI.getStats(id).then(res => res.data),
    { enabled: !!id }
  );

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

  const mockMatches = [
    {
      id: 1,
      opponent: 'John Smith',
      opponentSchool: 'Oklahoma State',
      result: 'W',
      decision: 'Decision',
      score: '7-2',
      tournament: '2024 NCAA Championships',
      round: 'Quarterfinals',
      date: '2024-03-21',
    },
    {
      id: 2,
      opponent: 'Mike Johnson',
      opponentSchool: 'Iowa',
      result: 'W',
      decision: 'Pin',
      score: 'Fall 2:15',
      tournament: '2024 NCAA Championships',
      round: 'Round of 16',
      date: '2024-03-20',
    },
    {
      id: 3,
      opponent: 'Dave Wilson',
      opponentSchool: 'Penn State',
      result: 'L',
      decision: 'Decision',
      score: '4-6',
      tournament: '2024 Big Ten Championships',
      round: 'Finals',
      date: '2024-03-10',
    },
  ];

  return (
    <Container maxWidth="lg">
      {/* Header */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h3" component="h1" gutterBottom>
              {wrestler.first_name} {wrestler.last_name}
            </Typography>
            <Typography variant="h5" color="text.secondary" gutterBottom>
              {wrestler.school?.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
              <Chip label={`${wrestler.weight_class} lbs`} color="primary" />
              <Chip label={wrestler.year || 'Senior'} variant="outlined" />
              {wrestler.hometown && wrestler.state && (
                <Chip label={`${wrestler.hometown}, ${wrestler.state}`} variant="outlined" />
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
                <strong>School:</strong> {wrestler.school?.name}
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Conference:</strong> {wrestler.school?.conference || 'N/A'}
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Weight Class:</strong> {wrestler.weight_class} lbs
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Year:</strong> {wrestler.year || 'N/A'}
              </Typography>
              {wrestler.hometown && wrestler.state && (
                <Typography variant="body1" paragraph>
                  <strong>Hometown:</strong> {wrestler.hometown}, {wrestler.state}
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
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Opponent</TableCell>
                      <TableCell>School</TableCell>
                      <TableCell>Result</TableCell>
                      <TableCell>Score</TableCell>
                      <TableCell>Tournament</TableCell>
                      <TableCell>Round</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockMatches.map((match) => (
                      <TableRow key={match.id}>
                        <TableCell>{match.date}</TableCell>
                        <TableCell>{match.opponent}</TableCell>
                        <TableCell>{match.opponentSchool}</TableCell>
                        <TableCell>
                          <Chip
                            label={match.result}
                            color={match.result === 'W' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{match.score}</TableCell>
                        <TableCell>{match.tournament}</TableCell>
                        <TableCell>{match.round}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default WrestlerPage;

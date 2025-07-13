import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
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
  Chip,
  Avatar,
  Link as MuiLink,
} from '@mui/material';
import { Link } from 'react-router-dom';
import { schoolsAPI } from '../services/api';

const SchoolPage = () => {
  const { id } = useParams();

  const { data: school, isLoading, error } = useQuery(
    ['school', id],
    () => schoolsAPI.getById(id).then(res => res.data),
    { enabled: !!id }
  );

  const { data: stats } = useQuery(
    ['school-stats', id],
    () => schoolsAPI.getStats(id).then(res => res.data),
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
        Error loading school data: {error.message}
      </Alert>
    );
  }

  if (!school) {
    return <Alert severity="info">School not found</Alert>;
  }

  // Mock data for coaches since they might not be loaded yet
  const mockCoaches = [
    {
      id: 1,
      first_name: 'John',
      last_name: 'Smith',
      position: 'Head Coach',
      years_experience: 15,
    },
    {
      id: 2,
      first_name: 'Mike',
      last_name: 'Johnson',
      position: 'Assistant Coach',
      years_experience: 8,
    },
  ];

  return (
    <Container maxWidth="lg">
      {/* Header */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={2}>
            {school.logo_url ? (
              <Avatar
                src={school.logo_url}
                alt={`${school.name} logo`}
                sx={{ width: 80, height: 80, mx: 'auto' }}
              />
            ) : (
              <Avatar sx={{ width: 80, height: 80, mx: 'auto', fontSize: '2rem' }}>
                {school.name.charAt(0)}
              </Avatar>
            )}
          </Grid>
          <Grid item xs={12} md={10}>
            <Typography variant="h3" component="h1" gutterBottom>
              {school.name}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
              {school.conference && (
                <Chip label={school.conference} color="primary" />
              )}
              {school.state && (
                <Chip label={school.state} variant="outlined" />
              )}
              {school.city && school.state && (
                <Chip label={`${school.city}, ${school.state}`} variant="outlined" />
              )}
            </Box>
            {school.website && (
              <Box sx={{ mt: 2 }}>
                <MuiLink href={school.website} target="_blank" rel="noopener noreferrer">
                  Visit School Website
                </MuiLink>
              </Box>
            )}
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={4}>
        {/* Team Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Team Statistics
              </Typography>
              {stats ? (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="h6" color="primary">
                      {stats.total_wrestlers}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Wrestlers
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6">
                      {stats.active_weight_classes.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Weight Classes
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6" color="success.main">
                      {stats.total_wins}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Team Wins
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6" color="error.main">
                      {stats.total_losses}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Team Losses
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6">
                      {stats.conference_championships}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Conference Titles
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="h6">
                      {stats.national_championships}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      National Titles
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

        {/* School Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                School Information
              </Typography>
              <Typography variant="body1" paragraph>
                <strong>Name:</strong> {school.name}
              </Typography>
              {school.conference && (
                <Typography variant="body1" paragraph>
                  <strong>Conference:</strong> {school.conference}
                </Typography>
              )}
              {school.city && (
                <Typography variant="body1" paragraph>
                  <strong>Location:</strong> {school.city}, {school.state}
                </Typography>
              )}
              {school.website && (
                <Typography variant="body1" paragraph>
                  <strong>Website:</strong>{' '}
                  <MuiLink href={school.website} target="_blank" rel="noopener noreferrer">
                    {school.website}
                  </MuiLink>
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Coaching Staff */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Coaching Staff
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Position</TableCell>
                      <TableCell>Experience</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mockCoaches.map((coach) => (
                      <TableRow key={coach.id}>
                        <TableCell>
                          <Link
                            to={`/coach/${coach.id}`}
                            style={{ textDecoration: 'none', color: 'inherit' }}
                          >
                            {coach.first_name} {coach.last_name}
                          </Link>
                        </TableCell>
                        <TableCell>{coach.position}</TableCell>
                        <TableCell>{coach.years_experience} years</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Current Roster */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Current Roster
              </Typography>
              {school.wrestlers && school.wrestlers.length > 0 ? (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Weight Class</TableCell>
                        <TableCell>Year</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {school.wrestlers.map((wrestler) => (
                        <TableRow key={wrestler.id}>
                          <TableCell>
                            <Link
                              to={`/wrestler/${wrestler.id}`}
                              style={{ textDecoration: 'none', color: 'inherit' }}
                            >
                              {wrestler.first_name} {wrestler.last_name}
                            </Link>
                          </TableCell>
                          <TableCell>{wrestler.weight_class} lbs</TableCell>
                          <TableCell>{wrestler.year || 'N/A'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography color="text.secondary">
                  No wrestlers found for this school
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SchoolPage;

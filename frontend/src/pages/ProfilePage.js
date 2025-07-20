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
  CircularProgress,
  Alert,
  Chip,
  Avatar,
} from '@mui/material';
import { Person, School, EmojiEvents } from '@mui/icons-material';
import { wrestlersAPI, schoolsAPI, tournamentsAPI } from '../services/api';
import { formatFullName, formatSchoolName, toTitleCase } from '../utils/formatters';

const ProfilePage = () => {
  const { id } = useParams();
  
  // Try to fetch data as different entity types
  const { data: wrestlerData, error: wrestlerError, isLoading: wrestlerLoading } = useQuery(
    ['wrestler', id],
    () => wrestlersAPI.getById(id),
    {
      retry: false,
      select: (response) => ({ ...response.data, entityType: 'wrestler' }),
    }
  );

  const { data: schoolData, error: schoolError, isLoading: schoolLoading } = useQuery(
    ['school', id],
    () => schoolsAPI.getById(id),
    {
      enabled: !wrestlerData && !wrestlerLoading,
      retry: false,
      select: (response) => ({ ...response.data, entityType: 'school' }),
    }
  );

  const { data: tournamentData, error: tournamentError, isLoading: tournamentLoading } = useQuery(
    ['tournament', id],
    () => tournamentsAPI.getById(id),
    {
      enabled: !wrestlerData && !schoolData && !wrestlerLoading && !schoolLoading,
      retry: false,
      select: (response) => ({ ...response.data, entityType: 'tournament' }),
    }
  );

  // Determine which data to use
  const profileData = wrestlerData || schoolData || tournamentData;
  const isLoading = wrestlerLoading || schoolLoading || tournamentLoading;
  const hasError = wrestlerError && schoolError && tournamentError;

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (hasError || !profileData) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          Profile not found. The requested ID "{id}" does not match any wrestler, school, or tournament.
        </Alert>
      </Container>
    );
  }

  const renderWrestlerProfile = (wrestler) => (
    <>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar sx={{ width: 80, height: 80, mr: 3, bgcolor: 'primary.main' }}>
              <Person sx={{ fontSize: 40 }} />
            </Avatar>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {wrestler.name || formatFullName(wrestler.first_name || '', wrestler.last_name || '')}
              </Typography>
              <Chip
                icon={<Person />}
                label="Wrestler"
                color="primary"
                sx={{ mb: 1 }}
              />
            </Box>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Personal Information
              </Typography>
              <Box component="dl" sx={{ mt: 0 }}>
                {wrestler.first_name && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      First Name:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {wrestler.first_name}
                    </Typography>
                  </>
                )}
                {wrestler.last_name && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      Last Name:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {wrestler.last_name}
                    </Typography>
                  </>
                )}
                {wrestler.date_of_birth && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      Date of Birth:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {new Date(wrestler.date_of_birth).toLocaleDateString()}
                    </Typography>
                  </>
                )}
                {wrestler.city_of_origin && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      City of Origin:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {wrestler.city_of_origin}
                    </Typography>
                  </>
                )}
                {wrestler.state_of_origin && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      State of Origin:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {wrestler.state_of_origin}
                    </Typography>
                  </>
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </>
  );

  const renderSchoolProfile = (school) => (
    <>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar sx={{ width: 80, height: 80, mr: 3, bgcolor: 'secondary.main' }}>
              <School sx={{ fontSize: 40 }} />
            </Avatar>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {formatSchoolName(school.name || '')}
              </Typography>
              <Chip
                icon={<School />}
                label="School"
                color="secondary"
                sx={{ mb: 1 }}
              />
            </Box>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                School Information
              </Typography>
              <Box component="dl" sx={{ mt: 0 }}>
                {school.location && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      Location:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {school.location}
                    </Typography>
                  </>
                )}
                {school.mascot && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      Mascot:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {school.mascot}
                    </Typography>
                  </>
                )}
                {school.school_type && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      School Type:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {toTitleCase(school.school_type)}
                    </Typography>
                  </>
                )}
                {school.school_url && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      Website:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      <a href={school.school_url} target="_blank" rel="noopener noreferrer">
                        {school.school_url}
                      </a>
                    </Typography>
                  </>
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </>
  );

  const renderTournamentProfile = (tournament) => (
    <>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
            <Avatar sx={{ width: 80, height: 80, mr: 3, bgcolor: 'warning.main' }}>
              <EmojiEvents sx={{ fontSize: 40 }} />
            </Avatar>
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                {tournament.name}
              </Typography>
              <Chip
                icon={<EmojiEvents />}
                label="Tournament"
                color="warning"
                sx={{ mb: 1 }}
              />
            </Box>
          </Box>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                Tournament Information
              </Typography>
              <Box component="dl" sx={{ mt: 0 }}>
                {tournament.date && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      Date:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {new Date(tournament.date).toLocaleDateString()}
                    </Typography>
                  </>
                )}
                {tournament.year && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      Year:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {tournament.year}
                    </Typography>
                  </>
                )}
                {tournament.location && (
                  <>
                    <Typography component="dt" variant="body2" color="text.secondary">
                      Location:
                    </Typography>
                    <Typography component="dd" variant="body1" sx={{ mb: 1 }}>
                      {tournament.location}
                    </Typography>
                  </>
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </>
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        {profileData.entityType === 'wrestler' && renderWrestlerProfile(profileData)}
        {profileData.entityType === 'school' && renderSchoolProfile(profileData)}
        {profileData.entityType === 'tournament' && renderTournamentProfile(profileData)}
        
        {/* Additional sections can be added here based on entity type */}
        <Paper sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Additional Information
          </Typography>
          <Typography variant="body2" color="text.secondary">
            More detailed information and related data will be displayed here based on the entity type.
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
};

export default ProfilePage;
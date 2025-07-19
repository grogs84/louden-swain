import React, { useState } from 'react';
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
  Tabs,
  Tab,
} from '@mui/material';
import { profileAPI } from '../services/api';
import { formatFullName, formatLocation } from '../utils/formatters';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`role-tabpanel-${index}`}
      aria-labelledby={`role-tab-${index}`}
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

function a11yProps(index) {
  return {
    id: `role-tab-${index}`,
    'aria-controls': `role-tabpanel-${index}`,
  };
}

const WrestlerStatsSection = ({ personId, roleType }) => {
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery(
    ['profile-stats', personId, roleType],
    () => profileAPI.getStats(personId, roleType).then(res => res.data),
    { 
      enabled: !!personId && !!roleType,
      staleTime: 0,
      cacheTime: 0
    }
  );

  const { data: matches, isLoading: matchesLoading, error: matchesError } = useQuery(
    ['profile-matches', personId, roleType],
    () => profileAPI.getMatches(personId, roleType, { limit: 10 }).then(res => res.data),
    { enabled: !!personId && !!roleType }
  );

  if (statsLoading) {
    return <CircularProgress />;
  }

  if (statsError) {
    return <Alert severity="error">Error loading wrestler stats: {statsError.message}</Alert>;
  }

  return (
    <Grid container spacing={4}>
      {/* Statistics */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Wrestling Statistics
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
                  <Typography variant="h6" color="secondary">
                    {stats.aa_count || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    All-American
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
              Wrestling Info
            </Typography>
            <Typography variant="body1" paragraph>
              <strong>Total Matches:</strong> {stats?.match_count || 0}
            </Typography>
            <Typography variant="body1" paragraph>
              <strong>Win Percentage:</strong> {stats?.win_percentage?.toFixed(1) || 0}%
            </Typography>
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
                      <TableCell>Round</TableCell>
                      <TableCell>Wrestler</TableCell>
                      <TableCell>Score</TableCell>
                      <TableCell>Opponent</TableCell>
                      <TableCell>Opp Score</TableCell>
                      <TableCell>Result</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {matches.map((match) => (
                      <TableRow key={match.match_id || match.id}>
                        <TableCell>{match.year}</TableCell>
                        <TableCell>{match.weight_class} lbs</TableCell>
                        <TableCell>{match.round}</TableCell>
                        <TableCell>{match.wrestler_name || formatFullName(match.opponent_first_name || '', match.opponent_last_name || '')}</TableCell>
                        <TableCell>{match.scored || match.score || '-'}</TableCell>
                        <TableCell>{match.opponent || formatFullName(match.opponent_first_name || '', match.opponent_last_name || '')}</TableCell>
                        <TableCell>{match.opponent_scored || '-'}</TableCell>
                        <TableCell>
                          <Chip
                            label={match.result_type || match.result || match.decision}
                            color={match.result === 'W' ? 'success' : 'error'}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
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
  );
};

const CoachStatsSection = ({ personId, roleType }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          Coaching Information
        </Typography>
        <Typography variant="body1">
          Coach statistics and information will be available soon.
        </Typography>
      </CardContent>
    </Card>
  );
};

const ProfilePage = () => {
  const { id } = useParams();
  const [selectedTab, setSelectedTab] = useState(0);

  const { data: profile, isLoading, error } = useQuery(
    ['profile', id],
    () => profileAPI.getById(id).then(res => res.data),
    { enabled: !!id }
  );

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

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
        Error loading profile data: {error.message}
      </Alert>
    );
  }

  if (!profile) {
    return <Alert severity="info">Profile not found</Alert>;
  }

  const getRoleDisplayName = (roleType) => {
    switch (roleType.toLowerCase()) {
      case 'wrestler':
        return 'Wrestler';
      case 'coach':
        return 'Coach';
      default:
        return roleType.charAt(0).toUpperCase() + roleType.slice(1);
    }
  };

  const renderRoleSection = (roleType, personId) => {
    switch (roleType.toLowerCase()) {
      case 'wrestler':
        return <WrestlerStatsSection personId={personId} roleType={roleType} />;
      case 'coach':
        return <CoachStatsSection personId={personId} roleType={roleType} />;
      default:
        return (
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                {getRoleDisplayName(roleType)} Information
              </Typography>
              <Typography variant="body1">
                Information for this role type is not yet available.
              </Typography>
            </CardContent>
          </Card>
        );
    }
  };

  return (
    <Container maxWidth="lg">
      {/* Header */}
      <Paper sx={{ p: 4, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={8}>
            <Typography variant="h3" component="h1" gutterBottom>
              {formatFullName(profile.first_name, profile.last_name)}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
              {profile.roles.map((role) => (
                <Chip
                  key={role.role_id}
                  label={getRoleDisplayName(role.role_type)}
                  color="primary"
                  variant="outlined"
                />
              ))}
              {profile.city_of_origin && profile.state_of_origin && (
                <Chip 
                  label={formatLocation(`${profile.city_of_origin}, ${profile.state_of_origin}`)} 
                  variant="outlined" 
                />
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Role-specific content */}
      {profile.roles && profile.roles.length > 0 ? (
        <>
          {profile.roles.length > 1 ? (
            // Multiple roles - show tabs
            <Box sx={{ width: '100%' }}>
              <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={selectedTab} onChange={handleTabChange} aria-label="role tabs">
                  {profile.roles.map((role, index) => (
                    <Tab
                      key={role.role_id}
                      label={getRoleDisplayName(role.role_type)}
                      {...a11yProps(index)}
                    />
                  ))}
                </Tabs>
              </Box>
              {profile.roles.map((role, index) => (
                <TabPanel key={role.role_id} value={selectedTab} index={index}>
                  {renderRoleSection(role.role_type, profile.person_id)}
                </TabPanel>
              ))}
            </Box>
          ) : (
            // Single role - show directly
            <Box>
              <Typography variant="h4" gutterBottom>
                {getRoleDisplayName(profile.roles[0].role_type)} Profile
              </Typography>
              {renderRoleSection(profile.roles[0].role_type, profile.person_id)}
            </Box>
          )}
        </>
      ) : (
        <Alert severity="info">
          No role information available for this person.
        </Alert>
      )}
    </Container>
  );
};

export default ProfilePage;
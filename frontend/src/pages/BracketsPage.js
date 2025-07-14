import React, { useState } from 'react';
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
} from '@mui/material';
import { tournamentsAPI, bracketsAPI } from '../services/api';

const BracketsPage = () => {
  const { tournamentId } = useParams();
  const [selectedTournament, setSelectedTournament] = useState(tournamentId || '');
  const [selectedWeightClass, setSelectedWeightClass] = useState('');

  const { data: tournaments, isLoading: tournamentsLoading } = useQuery(
    'tournaments',
    () => tournamentsAPI.getAll().then(res => res.data)
  );

  const { data: brackets, isLoading: bracketsLoading } = useQuery(
    ['brackets', selectedTournament],
    () => bracketsAPI.getByTournament(selectedTournament).then(res => res.data),
    { enabled: !!selectedTournament }
  );

  const { data: bracketData } = useQuery(
    ['bracket-data', selectedWeightClass],
    () => bracketsAPI.getData(selectedWeightClass).then(res => res.data),
    { enabled: !!selectedWeightClass }
  );

  // Mock tournament data if none exists
  const mockTournaments = tournaments || [
    { id: 1, name: '2024 NCAA D1 Wrestling Championships', year: 2024 },
    { id: 2, name: '2023 NCAA D1 Wrestling Championships', year: 2023 },
  ];

  // Mock bracket data for demonstration
  // eslint-disable-next-line no-unused-vars
  const mockBracketData = {
    rounds: [
      {
        title: 'Round 1',
        seeds: [
          {
            id: 1,
            date: '2024-03-21',
            teams: [
              { name: 'John Smith (Oklahoma State)', id: 1 },
              { name: 'Mike Johnson (Iowa)', id: 2 }
            ]
          },
          {
            id: 2,
            date: '2024-03-21',
            teams: [
              { name: 'Dave Wilson (Penn State)', id: 3 },
              { name: 'Tom Brown (Ohio State)', id: 4 }
            ]
          },
          {
            id: 3,
            date: '2024-03-21',
            teams: [
              { name: 'Steve Davis (Iowa State)', id: 5 },
              { name: 'Mark Taylor (Michigan)', id: 6 }
            ]
          },
          {
            id: 4,
            date: '2024-03-21',
            teams: [
              { name: 'Chris Miller (Nebraska)', id: 7 },
              { name: 'Jake Anderson (Wisconsin)', id: 8 }
            ]
          }
        ]
      },
      {
        title: 'Quarterfinals',
        seeds: [
          {
            id: 5,
            date: '2024-03-22',
            teams: [
              { name: 'John Smith (Oklahoma State)', id: 1 },
              { name: 'Dave Wilson (Penn State)', id: 3 }
            ]
          },
          {
            id: 6,
            date: '2024-03-22',
            teams: [
              { name: 'Steve Davis (Iowa State)', id: 5 },
              { name: 'Chris Miller (Nebraska)', id: 7 }
            ]
          }
        ]
      },
      {
        title: 'Semifinals',
        seeds: [
          {
            id: 7,
            date: '2024-03-23',
            teams: [
              { name: 'John Smith (Oklahoma State)', id: 1 },
              { name: 'Steve Davis (Iowa State)', id: 5 }
            ]
          }
        ]
      },
      {
        title: 'Finals',
        seeds: [
          {
            id: 8,
            date: '2024-03-24',
            teams: [
              { name: 'John Smith (Oklahoma State)', id: 1 },
              { name: 'TBD', id: null }
            ]
          }
        ]
      }
    ]
  };

  const weightClasses = [125, 133, 141, 149, 157, 165, 174, 184, 197, 285];

  if (tournamentsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h3" component="h1" gutterBottom>
        Tournament Brackets
      </Typography>

      {/* Tournament and Weight Class Selection */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Tournament</InputLabel>
              <Select
                value={selectedTournament}
                onChange={(e) => setSelectedTournament(e.target.value)}
                label="Tournament"
              >
                {mockTournaments.map((tournament) => (
                  <MenuItem key={tournament.id} value={tournament.id}>
                    {tournament.name} ({tournament.year})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth disabled={!selectedTournament}>
              <InputLabel>Weight Class</InputLabel>
              <Select
                value={selectedWeightClass}
                onChange={(e) => setSelectedWeightClass(e.target.value)}
                label="Weight Class"
              >
                {weightClasses.map((weight) => (
                  <MenuItem key={weight} value={weight}>
                    {weight} lbs
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Bracket Display */}
      {selectedTournament && selectedWeightClass ? (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              {selectedWeightClass} lbs Bracket
            </Typography>
            {bracketsLoading ? (
              <Box display="flex" justifyContent="center" py={4}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ overflow: 'auto', minHeight: '600px', p: 3 }}>
                <Paper sx={{ p: 3, textAlign: 'center' }}>
                  <Typography variant="h5" gutterBottom>
                    Tournament Bracket Visualization
                  </Typography>
                  <Typography variant="body1" color="text.secondary" paragraph>
                    Bracket visualization component will be implemented here.
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Selected Weight Class: {selectedWeightClass} lbs
                  </Typography>
                  {bracketData && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2">
                        Bracket data loaded successfully
                      </Typography>
                    </Box>
                  )}
                  {brackets && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Available brackets: {brackets.length}
                      </Typography>
                    </Box>
                  )}
                </Paper>
              </Box>
            )}
          </CardContent>
        </Card>
      ) : (
        <Alert severity="info" sx={{ mt: 4 }}>
          Please select a tournament and weight class to view the bracket.
        </Alert>
      )}

      {/* Weight Class Overview */}
      {selectedTournament && !selectedWeightClass && (
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              Available Weight Classes
            </Typography>
            <Grid container spacing={2}>
              {weightClasses.map((weight) => (
                <Grid item xs={6} sm={4} md={3} lg={2} key={weight}>
                  <Card 
                    sx={{ 
                      cursor: 'pointer',
                      transition: 'transform 0.2s',
                      '&:hover': {
                        transform: 'translateY(-2px)',
                      },
                    }}
                    onClick={() => setSelectedWeightClass(weight)}
                  >
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h6">
                        {weight} lbs
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default BracketsPage;

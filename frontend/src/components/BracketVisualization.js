import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Paper,
  useTheme
} from '@mui/material';

const MatchCard = ({ match, roundIndex, isWinner }) => {
  const theme = useTheme();
  
  return (
    <Card 
      sx={{ 
        mb: 2, 
        minWidth: 200,
        border: isWinner ? `2px solid ${theme.palette.success.main}` : '1px solid #ddd',
        backgroundColor: isWinner ? theme.palette.success.light : 'inherit'
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        <Typography variant="caption" color="text.secondary" gutterBottom>
          {match.date}
        </Typography>
        {match.teams && match.teams.map((team, index) => (
          <Box key={team.id || index} sx={{ mb: 0.5 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: team.isWinner ? 'bold' : 'normal',
                  color: team.isWinner ? theme.palette.success.dark : 'inherit'
                }}
              >
                {team.name}
              </Typography>
              {team.isWinner && (
                <Chip 
                  label="W" 
                  size="small" 
                  color="success" 
                  sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
                />
              )}
            </Box>
          </Box>
        ))}
        {match.score && (
          <Typography variant="caption" color="text.secondary">
            Score: {match.score}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const RoundColumn = ({ round, roundIndex, totalRounds }) => {
  const theme = useTheme();
  
  return (
    <Box sx={{ minWidth: 220, px: 1 }}>
      <Typography 
        variant="h6" 
        align="center" 
        gutterBottom 
        sx={{ 
          mb: 3,
          color: theme.palette.primary.main,
          fontWeight: 'bold'
        }}
      >
        {round.title}
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {round.seeds && round.seeds.map((match, matchIndex) => {
          const isWinner = roundIndex === totalRounds - 1; // Finals winner
          return (
            <MatchCard 
              key={match.id || matchIndex} 
              match={match} 
              roundIndex={roundIndex}
              isWinner={isWinner && match.teams?.some(team => team.isWinner)}
            />
          );
        })}
      </Box>
    </Box>
  );
};

const BracketVisualization = ({ bracketData, weightClass }) => {
  const theme = useTheme();
  
  if (!bracketData || !bracketData.rounds || bracketData.rounds.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No bracket data available for {weightClass} lbs
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Please select a tournament and weight class to view the bracket.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ width: '100%', overflow: 'auto' }}>
      <Typography variant="h4" align="center" gutterBottom sx={{ mb: 4 }}>
        {weightClass} lbs Tournament Bracket
      </Typography>
      
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'flex-start',
          alignItems: 'flex-start',
          minWidth: 'fit-content',
          gap: 2,
          pb: 2
        }}
      >
        {bracketData.rounds.map((round, index) => (
          <RoundColumn 
            key={index} 
            round={round} 
            roundIndex={index}
            totalRounds={bracketData.rounds.length}
          />
        ))}
      </Box>
      
      <Box sx={{ mt: 4, p: 2, backgroundColor: theme.palette.grey[100], borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary" align="center">
          Tournament bracket visualization • Scroll horizontally to view all rounds
        </Typography>
      </Box>
    </Box>
  );
};

export default BracketVisualization;
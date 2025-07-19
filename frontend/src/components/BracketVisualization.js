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

const MatchCard = ({ match, roundIndex, isWinner, isChampionship }) => {
  const theme = useTheme();
  
  const cardSx = {
    mb: 2, 
    minWidth: { xs: 160, sm: 200 },
    border: isWinner ? `2px solid ${theme.palette.success.main}` : '1px solid #ddd',
    backgroundColor: isWinner ? theme.palette.success.light : 'inherit',
    transition: 'all 0.2s ease-in-out',
    '&:hover': {
      boxShadow: theme.shadows[4],
      transform: 'translateY(-1px)',
    }
  };

  if (isChampionship) {
    cardSx.border = `3px solid ${theme.palette.warning.main}`;
    cardSx.backgroundColor = theme.palette.warning.light;
  }
  
  return (
    <Card sx={cardSx}>
      <CardContent sx={{ p: { xs: 1.5, sm: 2 }, '&:last-child': { pb: { xs: 1.5, sm: 2 } } }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="caption" color="text.secondary" sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem' } }}>
            {match.date}
          </Typography>
          {isChampionship && (
            <Chip 
              label="🏆" 
              size="small" 
              color="warning" 
              sx={{ fontSize: '0.7rem', height: 20, minWidth: 20 }}
            />
          )}
        </Box>
        {match.teams && match.teams.map((team, index) => (
          <Box key={team.id || index} sx={{ mb: 0.5 }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: team.isWinner ? 'bold' : 'normal',
                  color: team.isWinner ? theme.palette.success.dark : 'inherit',
                  flex: 1,
                  pr: 1,
                  fontSize: { xs: '0.75rem', sm: '0.875rem' },
                  lineHeight: 1.3
                }}
              >
                {team.name}
              </Typography>
              {team.isWinner && (
                <Chip 
                  label="W" 
                  size="small" 
                  color="success" 
                  sx={{ ml: 1, height: 18, fontSize: '0.6rem', minWidth: 20 }}
                />
              )}
            </Box>
          </Box>
        ))}
        {match.score && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block', fontSize: '0.65rem' }}>
            Score: {match.score}
          </Typography>
        )}
        {match.result && (
          <Typography variant="caption" color="primary" sx={{ mt: 1, display: 'block', fontStyle: 'italic', fontSize: '0.65rem' }}>
            {match.result}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const RoundColumn = ({ round, roundIndex, totalRounds }) => {
  const theme = useTheme();
  const isChampionshipRound = roundIndex === totalRounds - 1;
  
  return (
    <Box sx={{ minWidth: { xs: 180, sm: 220 }, px: { xs: 0.5, sm: 1 } }}>
      <Typography 
        variant="h6" 
        align="center" 
        gutterBottom 
        sx={{ 
          mb: 3,
          color: isChampionshipRound ? theme.palette.warning.main : theme.palette.primary.main,
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: 0.5,
          fontSize: { xs: '0.9rem', sm: '1.25rem' }
        }}
      >
        {round.title}
      </Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        {round.seeds && round.seeds.map((match, matchIndex) => {
          const hasWinner = match.teams?.some(team => team.isWinner);
          return (
            <MatchCard 
              key={match.id || matchIndex} 
              match={match} 
              roundIndex={roundIndex}
              isWinner={hasWinner}
              isChampionship={isChampionshipRound && hasWinner}
            />
          );
        })}
      </Box>
    </Box>
  );
};

const BracketVisualization = ({ bracketData, weightClass }) => {
  const theme = useTheme();
  
  if (!bracketData) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Loading bracket data...
        </Typography>
      </Paper>
    );
  }

  if (bracketData.error) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="error">
          Error loading bracket data
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {bracketData.error}
        </Typography>
      </Paper>
    );
  }
  
  if (!bracketData.rounds || bracketData.rounds.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No bracket data available for {weightClass} lbs
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          This tournament bracket may not have been set up yet.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box sx={{ width: '100%', overflow: 'auto' }}>
      <Typography 
        variant="h4" 
        align="center" 
        gutterBottom 
        sx={{ 
          mb: 4,
          color: theme => theme.palette.primary.main,
          fontWeight: 'bold',
          fontSize: { xs: '1.5rem', sm: '2rem', md: '2.125rem' }
        }}
      >
        {weightClass} lbs Tournament Bracket
      </Typography>
      
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: { xs: 'flex-start', lg: 'center' },
          alignItems: 'flex-start',
          minWidth: 'fit-content',
          gap: { xs: 1, sm: 2 },
          pb: 2,
          px: { xs: 1, sm: 2 }
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
      
      <Box 
        sx={{ 
          mt: 4, 
          p: 2, 
          backgroundColor: theme.palette.grey[100], 
          borderRadius: 1,
          mx: { xs: 1, sm: 2 }
        }}
      >
        <Typography variant="body2" color="text.secondary" align="center">
          Tournament bracket visualization • {bracketData.rounds.length > 2 ? 'Scroll horizontally to view all rounds' : 'Complete bracket view'}
        </Typography>
        {bracketData.tournament_id && (
          <Typography variant="caption" color="text.secondary" align="center" display="block" sx={{ mt: 0.5 }}>
            Tournament ID: {bracketData.tournament_id} • Weight Class: {bracketData.weight_class} lbs
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default BracketVisualization;
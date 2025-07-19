import React from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Paper,
} from '@mui/material';
import { Link } from 'react-router-dom';
import { 
  EmojiEvents, 
  School, 
  Person, 
  Search 
} from '@mui/icons-material';

const HomePage = () => {
  const features = [
    {
      icon: <EmojiEvents sx={{ fontSize: 60 }} />,
      title: 'Tournament Brackets',
      description: 'View interactive NCAA D1 Wrestling Championship brackets with detailed match results and progression.',
      link: '/brackets',
      buttonText: 'View Brackets',
    },
    {
      icon: <Person sx={{ fontSize: 60 }} />,
      title: 'Wrestler Profiles',
      description: 'Explore detailed wrestler profiles including statistics, match history, and career highlights.',
      link: '/search?type=wrestlers',
      buttonText: 'Find Wrestlers',
    },
    {
      icon: <School sx={{ fontSize: 60 }} />,
      title: 'School Programs',
      description: 'Discover wrestling programs, team statistics, coaching staff, and school achievements.',
      link: '/search?type=schools',
      buttonText: 'Browse Schools',
    },
    {
      icon: <Search sx={{ fontSize: 60 }} />,
      title: 'Advanced Search',
      description: 'Search across wrestlers, schools, and coaches with powerful filtering options.',
      link: '/search',
      buttonText: 'Start Searching',
    },
  ];

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box sx={{ textAlign: 'center', my: 6 }}>
        <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Wrestling Data Hub
        </Typography>
        <Typography variant="h5" color="text.secondary" paragraph sx={{ maxWidth: 800, mx: 'auto' }}>
          Your comprehensive source for NCAA Division I Wrestling Championship data, 
          statistics, and tournament brackets. Explore wrestler profiles, school programs, 
          and championship history all in one place.
        </Typography>
        <Box sx={{ mt: 4 }}>
          {/* remove this button */ }
          {/* <Button
            variant="contained"
            size="large"
            component={Link}
            to="/brackets"
            sx={{ mr: 2, mb: 2 }}
          >
            View Latest Brackets
          </Button> */}
          <Button
            variant="outlined"
            size="large"
            component={Link}
            to="/search"
            sx={{ mb: 2 }}
          >
            Search Database
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box sx={{ my: 8 }}>
        <Typography variant="h3" component="h2" textAlign="center" gutterBottom sx={{ mb: 6 }}>
          Features
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1, textAlign: 'center', pt: 4 }}>
                  <Box sx={{ color: 'primary.main', mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography variant="h5" component="h3" gutterBottom>
                    {feature.title}
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
                <CardActions sx={{ justifyContent: 'center', pb: 3 }}>
                  <Button
                    variant="contained"
                    component={Link}
                    to={feature.link}
                  >
                    {feature.buttonText}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* About Section */}
      <Paper sx={{ p: 6, my: 8, backgroundColor: 'grey.50' }}>
        <Typography variant="h4" component="h2" textAlign="center" gutterBottom>
          About Wrestling Data Hub
        </Typography>
        <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
          Wrestling Data Hub is the definitive resource for NCAA Division I Wrestling Championship 
          information. Our platform provides comprehensive data on wrestlers, coaches, schools, and 
          tournament results, making it easy to track the sport's most compelling stories and statistics.
        </Typography>
        <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.8 }}>
          Whether you're a fan following your favorite wrestler's journey to the championship, 
          a coach analyzing competition, or a researcher studying the sport's evolution, 
          Wrestling Data Hub offers the tools and data you need.
        </Typography>
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Data Coverage Includes:
          </Typography>
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">• Wrestler Profiles</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">• Match Results</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">• Tournament Brackets</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">• School Programs</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">• Coaching Staff</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">• Historical Data</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">• Statistics</Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="body2">• Rankings</Typography>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default HomePage;

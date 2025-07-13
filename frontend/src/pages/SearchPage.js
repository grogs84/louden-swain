import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  Alert,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Search as SearchIcon, Person, School, EmojiEvents } from '@mui/icons-material';
import { searchAPI } from '../services/api';

const SearchPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [searchType, setSearchType] = useState(searchParams.get('type') || 'all');
  const [activeTab, setActiveTab] = useState(0);
  const [filters, setFilters] = useState({
    weightClass: '',
    conference: '',
    state: '',
  });

  const { data: searchResults, isLoading, error, refetch } = useQuery(
    ['search', searchQuery, searchType, filters],
    () => {
      if (!searchQuery.trim()) return null;
      
      if (searchType === 'wrestlers') {
        return searchAPI.searchWrestlers(searchQuery, {
          weight_class: filters.weightClass || undefined,
        }).then(res => ({ wrestlers: res.data, schools: [], coaches: [] }));
      } else if (searchType === 'schools') {
        return searchAPI.searchSchools(searchQuery, {
          conference: filters.conference || undefined,
          state: filters.state || undefined,
        }).then(res => ({ wrestlers: [], schools: res.data, coaches: [] }));
      } else {
        return searchAPI.searchAll(searchQuery).then(res => res.data);
      }
    },
    { enabled: false }
  );

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      const params = new URLSearchParams();
      params.set('q', searchQuery.trim());
      if (searchType !== 'all') params.set('type', searchType);
      setSearchParams(params);
      refetch();
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const weightClasses = [125, 133, 141, 149, 157, 165, 174, 184, 197, 285];
  const conferences = ['Big Ten', 'Big 12', 'Pac-12', 'ACC', 'SEC', 'MAC', 'EIWA'];
  const states = ['IA', 'PA', 'OK', 'OH', 'NE', 'WI', 'MN', 'IL', 'IN', 'MI'];

  useEffect(() => {
    const query = searchParams.get('q');
    const type = searchParams.get('type');
    if (query) {
      setSearchQuery(query);
      if (type) setSearchType(type);
      refetch();
    }
  }, [searchParams, refetch]);

  const renderSearchResults = () => {
    if (!searchResults) return null;

    const tabs = [
      { label: `All Results`, count: (searchResults.wrestlers?.length || 0) + (searchResults.schools?.length || 0) + (searchResults.coaches?.length || 0) },
      { label: `Wrestlers (${searchResults.wrestlers?.length || 0})`, count: searchResults.wrestlers?.length || 0 },
      { label: `Schools (${searchResults.schools?.length || 0})`, count: searchResults.schools?.length || 0 },
      { label: `Coaches (${searchResults.coaches?.length || 0})`, count: searchResults.coaches?.length || 0 },
    ];

    const renderResultsList = (results, type) => {
      if (!results || results.length === 0) {
        return (
          <Typography color="text.secondary" sx={{ p: 2 }}>
            No {type} found matching your search.
          </Typography>
        );
      }

      return (
        <List>
          {results.map((result) => (
            <ListItem
              key={`${result.type}-${result.id}`}
              component={Link}
              to={`/${result.type}/${result.id}`}
              sx={{
                textDecoration: 'none',
                color: 'inherit',
                borderBottom: '1px solid #eee',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {result.type === 'wrestler' && <Person fontSize="small" />}
                    {result.type === 'school' && <School fontSize="small" />}
                    {result.type === 'coach' && <EmojiEvents fontSize="small" />}
                    {result.name}
                  </Box>
                }
                secondary={result.additional_info}
              />
              <Chip
                label={result.type}
                size="small"
                color={
                  result.type === 'wrestler' ? 'primary' :
                  result.type === 'school' ? 'secondary' :
                  'default'
                }
              />
            </ListItem>
          ))}
        </List>
      );
    };

    return (
      <Paper sx={{ mt: 4 }}>
        <Tabs value={activeTab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          {tabs.map((tab, index) => (
            <Tab key={index} label={tab.label} />
          ))}
        </Tabs>

        <Box sx={{ p: 2 }}>
          {activeTab === 0 && (
            <Grid container spacing={3}>
              {searchResults.wrestlers && searchResults.wrestlers.length > 0 && (
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" gutterBottom>Wrestlers</Typography>
                  {renderResultsList(searchResults.wrestlers, 'wrestlers')}
                </Grid>
              )}
              {searchResults.schools && searchResults.schools.length > 0 && (
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" gutterBottom>Schools</Typography>
                  {renderResultsList(searchResults.schools, 'schools')}
                </Grid>
              )}
              {searchResults.coaches && searchResults.coaches.length > 0 && (
                <Grid item xs={12} md={4}>
                  <Typography variant="h6" gutterBottom>Coaches</Typography>
                  {renderResultsList(searchResults.coaches, 'coaches')}
                </Grid>
              )}
            </Grid>
          )}
          {activeTab === 1 && renderResultsList(searchResults.wrestlers, 'wrestlers')}
          {activeTab === 2 && renderResultsList(searchResults.schools, 'schools')}
          {activeTab === 3 && renderResultsList(searchResults.coaches, 'coaches')}
        </Box>
      </Paper>
    );
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h3" component="h1" gutterBottom>
        Search
      </Typography>

      {/* Search Form */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSearch}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Search wrestlers, schools, coaches..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Search Type</InputLabel>
                <Select
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value)}
                  label="Search Type"
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="wrestlers">Wrestlers</MenuItem>
                  <MenuItem value="schools">Schools</MenuItem>
                  <MenuItem value="coaches">Coaches</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                fullWidth
                disabled={!searchQuery.trim()}
              >
                Search
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {/* Filters */}
      {(searchType === 'wrestlers' || searchType === 'schools') && (
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          <Grid container spacing={3}>
            {searchType === 'wrestlers' && (
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Weight Class</InputLabel>
                  <Select
                    value={filters.weightClass}
                    onChange={(e) => setFilters({ ...filters, weightClass: e.target.value })}
                    label="Weight Class"
                  >
                    <MenuItem value="">All Weight Classes</MenuItem>
                    {weightClasses.map((weight) => (
                      <MenuItem key={weight} value={weight}>
                        {weight} lbs
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}
            {searchType === 'schools' && (
              <>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Conference</InputLabel>
                    <Select
                      value={filters.conference}
                      onChange={(e) => setFilters({ ...filters, conference: e.target.value })}
                      label="Conference"
                    >
                      <MenuItem value="">All Conferences</MenuItem>
                      {conferences.map((conference) => (
                        <MenuItem key={conference} value={conference}>
                          {conference}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>State</InputLabel>
                    <Select
                      value={filters.state}
                      onChange={(e) => setFilters({ ...filters, state: e.target.value })}
                      label="State"
                    >
                      <MenuItem value="">All States</MenuItem>
                      {states.map((state) => (
                        <MenuItem key={state} value={state}>
                          {state}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </>
            )}
          </Grid>
        </Paper>
      )}

      {/* Loading State */}
      {isLoading && (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Error searching: {error.message}
        </Alert>
      )}

      {/* Search Results */}
      {renderSearchResults()}

      {/* Quick Search Cards */}
      {!searchQuery && (
        <Grid container spacing={3} sx={{ mt: 4 }}>
          <Grid item xs={12}>
            <Typography variant="h5" gutterBottom>
              Quick Search
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Person sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
                  <Typography variant="h6">
                    Find Wrestlers
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Search for wrestlers by name, weight class, or school
                </Typography>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setSearchType('wrestlers');
                    setSearchQuery('');
                  }}
                >
                  Search Wrestlers
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <School sx={{ mr: 2, fontSize: 40, color: 'secondary.main' }} />
                  <Typography variant="h6">
                    Browse Schools
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Explore wrestling programs by school name, conference, or state
                </Typography>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setSearchType('schools');
                    setSearchQuery('');
                  }}
                >
                  Search Schools
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <EmojiEvents sx={{ mr: 2, fontSize: 40, color: 'warning.main' }} />
                  <Typography variant="h6">
                    Find Coaches
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  Look up coaching staff by name or school affiliation
                </Typography>
                <Button
                  variant="outlined"
                  onClick={() => {
                    setSearchType('coaches');
                    setSearchQuery('');
                  }}
                >
                  Search Coaches
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default SearchPage;

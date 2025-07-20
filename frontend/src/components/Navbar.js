import React, { useState, useEffect, useRef } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  InputBase,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  alpha,
  CircularProgress,
  Popper,
  ClickAwayListener,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { Search as SearchIcon, Menu as MenuIcon, Person, School, EmojiEvents } from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { searchAPI } from '../services/api';

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(1),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  width: '100%',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    [theme.breakpoints.up('sm')]: {
      width: '14ch',
      '&:focus': {
        width: '24ch',
      },
    },
  },
}));

const Navbar = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();
  const searchRef = useRef(null);
  const anchorRef = useRef(null);

  // Debounced search query
  const [debouncedQuery, setDebouncedQuery] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Live search results
  const { data: searchResults, isLoading } = useQuery(
    ['liveSearch', debouncedQuery],
    () => searchAPI.searchAll(debouncedQuery, { limit: 5 }),
    {
      enabled: debouncedQuery.length >= 2,
      select: (response) => response.data,
    }
  );

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setShowDropdown(false);
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    setShowDropdown(value.length >= 2);
  };

  const handleResultClick = (result) => {
    const route = result.type === 'wrestler' ? `/profile/${result.id}` :
                  result.type === 'school' ? `/profile/${result.id}` :
                  result.type === 'tournament' ? `/profile/${result.id}` :
                  `/profile/${result.id}`;
    
    navigate(route);
    setSearchQuery('');
    setShowDropdown(false);
  };

  const handleClickAway = () => {
    setShowDropdown(false);
  };

  const getResultIcon = (type) => {
    switch (type) {
      case 'wrestler':
        return <Person fontSize="small" />;
      case 'school':
        return <School fontSize="small" />;
      case 'tournament':
        return <EmojiEvents fontSize="small" />;
      default:
        return <Person fontSize="small" />;
    }
  };

  const hasResults = searchResults && (
    searchResults.wrestlers?.length > 0 ||
    searchResults.schools?.length > 0 ||
    searchResults.tournaments?.length > 0
  );

  const allResults = searchResults ? [
    ...(searchResults.wrestlers || []).slice(0, 3),
    ...(searchResults.schools || []).slice(0, 3),
    ...(searchResults.tournaments || []).slice(0, 3),
  ] : [];

  return (
    <AppBar position="static">
      <Toolbar>
        <IconButton
          size="large"
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        
        <Typography
          variant="h6"
          component={Link}
          to="/"
          sx={{
            flexGrow: 1,
            textDecoration: 'none',
            color: 'inherit',
            fontWeight: 'bold',
          }}
        >
          Wrestling Data Hub
        </Typography>

        <Box sx={{ display: { xs: 'none', sm: 'flex' }, mr: 2 }}>
          <Button color="inherit" component={Link} to="/">
            Home
          </Button>
          <Button color="inherit" component={Link} to="/brackets">
            Brackets
          </Button>
          <Button color="inherit" component={Link} to="/search">
            Search
          </Button>
        </Box>

        <ClickAwayListener onClickAway={handleClickAway}>
          <Box sx={{ position: 'relative' }}>
            <Search ref={anchorRef}>
              <SearchIconWrapper>
                <SearchIcon />
              </SearchIconWrapper>
              <form onSubmit={handleSearch}>
                <StyledInputBase
                  placeholder="Search wrestlers, schools..."
                  inputProps={{ 'aria-label': 'search' }}
                  value={searchQuery}
                  onChange={handleInputChange}
                  ref={searchRef}
                />
              </form>
            </Search>
            
            {/* Live Search Dropdown */}
            <Popper
              open={showDropdown && (hasResults || isLoading)}
              anchorEl={anchorRef.current}
              placement="bottom-start"
              style={{ zIndex: 1300, width: anchorRef.current?.offsetWidth }}
            >
              <Paper elevation={4} sx={{ maxHeight: 300, overflow: 'auto' }}>
                {isLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                    <CircularProgress size={20} />
                  </Box>
                ) : hasResults ? (
                  <List dense>
                    {allResults.slice(0, 8).map((result, index) => (
                      <ListItem
                        key={`${result.type}-${result.id}-${index}`}
                        button
                        onClick={() => handleResultClick(result)}
                        sx={{
                          cursor: 'pointer',
                          '&:hover': {
                            backgroundColor: 'action.hover',
                          },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          {getResultIcon(result.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={result.name}
                          secondary={result.additional_info}
                          sx={{
                            '& .MuiListItemText-primary': {
                              fontSize: '0.875rem',
                            },
                            '& .MuiListItemText-secondary': {
                              fontSize: '0.75rem',
                            },
                          }}
                        />
                      </ListItem>
                    ))}
                    {allResults.length > 8 && (
                      <ListItem 
                        button 
                        onClick={handleSearch}
                        sx={{ justifyContent: 'center', fontStyle: 'italic' }}
                      >
                        <ListItemText 
                          primary={`View all results for "${searchQuery}"`}
                          sx={{ textAlign: 'center' }}
                        />
                      </ListItem>
                    )}
                  </List>
                ) : null}
              </Paper>
            </Popper>
          </Box>
        </ClickAwayListener>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

/**
 * Utility functions for formatting text and data
 */

/**
 * Convert a string to title case (capitalize the first letter of each word)
 * @param {string} str - The string to convert
 * @returns {string} - The title case string
 */
export const toTitleCase = (str) => {
  if (!str) return '';
  
  return str
    .toLowerCase()
    .split(' ')
    .map(word => {
      // Handle special cases for common abbreviations and prepositions
      const lowercaseWords = ['of', 'the', 'and', 'in', 'on', 'at', 'to', 'for', 'with', 'by'];
      const uppercaseWords = ['ii', 'iii', 'iv', 'jr', 'sr'];
      
      if (lowercaseWords.includes(word.toLowerCase()) && word !== str.split(' ')[0]) {
        return word.toLowerCase();
      }
      
      if (uppercaseWords.includes(word.toLowerCase())) {
        return word.toUpperCase();
      }
      
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(' ');
};

/**
 * Format a full name (first + last) to title case
 * @param {string} firstName - First name
 * @param {string} lastName - Last name
 * @returns {string} - Formatted full name
 */
export const formatFullName = (firstName, lastName) => {
  const formattedFirst = toTitleCase(firstName);
  const formattedLast = toTitleCase(lastName);
  return `${formattedFirst} ${formattedLast}`.trim();
};

/**
 * Format school or organization name to title case
 * @param {string} name - School or organization name
 * @returns {string} - Formatted name
 */
export const formatSchoolName = (name) => {
  if (!name) return '';
  
  // Special handling for common university/college patterns
  return name
    .split(' ')
    .map(word => {
      // Keep certain words lowercase unless they're the first word
      const lowercaseWords = ['of', 'the', 'and', 'in', 'on', 'at', 'to', 'for', 'with', 'by'];
      // Keep certain abbreviations uppercase
      const uppercaseWords = ['usa', 'usc', 'ucla', 'mit', 'nyc', 'dc'];
      
      if (lowercaseWords.includes(word.toLowerCase()) && word !== name.split(' ')[0]) {
        return word.toLowerCase();
      }
      
      if (uppercaseWords.includes(word.toLowerCase())) {
        return word.toUpperCase();
      }
      
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(' ');
};

/**
 * Format location (city, state) to title case
 * @param {string} location - Location string
 * @returns {string} - Formatted location
 */
export const formatLocation = (location) => {
  return toTitleCase(location);
};

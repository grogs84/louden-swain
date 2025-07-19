# 🗄️ Supabase Database Schema

This document describes the actual database schema in our Supabase PostgreSQL instance.

## Tables Overview

### `person`
Core table for all people (wrestlers and coaches).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| person_id | TEXT | PRIMARY KEY | Unique text identifier |
| first_name | TEXT | NOT NULL | Person's first name |
| last_name | TEXT | NOT NULL | Person's last name |
| search_name | TEXT | | Optimized search field |
| date_of_birth | DATE | | Person's birth date |
| city_of_origin | TEXT | | Birth/origin city |
| state_of_origin | TEXT | | Birth/origin state |

### `role`
Defines roles (wrestler/coach) for people.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| role_id | TEXT | PRIMARY KEY | Unique text identifier |
| person_id | TEXT | NOT NULL, FK → person.person_id | Reference to person |
| role_type | TEXT | CHECK (wrestler/coach) | Role type constraint |

### `school`
Educational institutions participating in wrestling.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| school_id | TEXT | PRIMARY KEY | Unique text identifier |
| name | TEXT | NOT NULL | School name |
| location | TEXT | | School location |
| mascot | TEXT | | School mascot |
| school_type | TEXT | | Type of institution |
| school_url | TEXT | | School website URL |

### `tournament`
Wrestling tournaments and competitions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| tournament_id | TEXT | PRIMARY KEY | Unique text identifier |
| name | TEXT | NOT NULL | Tournament name |
| date | DATE | NOT NULL | Tournament date |
| year | INTEGER | | Tournament year |
| location | TEXT | | Tournament location |

### `participant`
Links roles to tournaments with participation details.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| participant_id | TEXT | PRIMARY KEY | Unique text identifier |
| role_id | TEXT | NOT NULL, FK → role.role_id | Reference to role |
| school_id | TEXT | NOT NULL, FK → school.school_id | School they represented |
| year | INTEGER | NOT NULL | Year of participation |
| weight_class | TEXT | NOT NULL | Weight class |
| seed | INTEGER | | Tournament seeding |

### `match`
Individual wrestling matches.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| match_id | TEXT | PRIMARY KEY | Unique text identifier |
| round | TEXT | NOT NULL | Tournament round |
| round_order | INTEGER | NOT NULL | Order within round |
| bracket_order | INTEGER | NOT NULL | Position in bracket |
| tournament_id | TEXT | NOT NULL, FK → tournament.tournament_id | Tournament reference |
| result_type | TEXT | | Type of result |
| fall_time | TEXT | | Time of fall (if applicable) |
| tech_time | TEXT | | Time of tech fall (if applicable) |
| winner_id | TEXT | FK → participant.participant_id | Winner reference |

### `participant_match`
Junction table linking participants to matches.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| match_id | TEXT | PRIMARY KEY (composite) | Match reference |
| participant_id | TEXT | PRIMARY KEY (composite) | Participant reference |
| is_winner | BOOLEAN | | Whether this participant won |
| score | INTEGER | | Individual score |
| next_match_id | TEXT | FK → match.match_id | Next match in bracket |

## Relationships

```
people (1) ←→ (many) participants
schools (1) ←→ (many) participants  
tournaments (1) ←→ (many) participants
tournaments (1) ←→ (many) matches
people (1) ←→ (many) matches (as winner)
people (1) ←→ (many) matches (as loser)
```

## Common Queries

### Search wrestlers by name
```sql
SELECT id, first_name, last_name, graduation_year, weight_class
FROM people 
WHERE LOWER(first_name || ' ' || last_name) LIKE LOWER('%search_term%')
ORDER BY last_name, first_name;
```

### Get wrestler's match history
```sql
SELECT m.*, t.name as tournament_name, t.year,
       w.first_name || ' ' || w.last_name as winner_name,
       l.first_name || ' ' || l.last_name as loser_name
FROM matches m
JOIN tournaments t ON m.tournament_id = t.id
JOIN people w ON m.winner_id = w.id  
JOIN people l ON m.loser_id = l.id
WHERE m.winner_id = ? OR m.loser_id = ?
ORDER BY t.year DESC, m.match_date DESC;
```

### Get school's wrestlers by year
```sql
SELECT DISTINCT p.*, part.weight_class, t.year
FROM people p
JOIN participants part ON p.id = part.person_id
JOIN tournaments t ON part.tournament_id = t.id
JOIN schools s ON part.school_id = s.id
WHERE s.id = ? AND t.year = ?
ORDER BY part.weight_class::INTEGER, p.last_name;
```

## Notes

- All timestamps are stored in UTC
- Weight classes are stored as strings (e.g., "125", "133", "285")
- State codes follow standard two-letter format (IA, PA, CA, etc.)
- Tournament divisions typically: "D1", "D2", "D3", "NAIA", "JUCO"
- Match types: "Decision", "Major Decision", "Tech Fall", "Fall", "Forfeit", "Disqualification"

## Schema Updates

To update this schema documentation:
1. Make changes in Supabase dashboard
2. Update this file with the changes
3. Commit to version control
4. Update backend models/queries as needed

## Schema Visualization

The Supabase database schema includes the following tables and relationships:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   person    │    │     role     │    │ participant │
│             │    │              │    │             │
│ person_id   │◄──►│ role_id      │◄──►│participant_id│
│ first_name  │    │ person_id    │    │ role_id     │
│ last_name   │    │ role_type    │    │ school_id   │
│ search_name │    │              │    │ year        │
│ date_of_birth│   └──────────────┘    │ weight_class│
│ city_of_origin│                      │ seed        │
│ state_of_origin│                     └─────────────┘
└─────────────┘                              │
                                             │
┌─────────────┐    ┌──────────────┐         │
│   school    │    │ tournament   │         │
│             │    │              │         │
│ school_id   │◄──►│tournament_id │◄────────┤
│ name        │    │ name         │         │
│ location    │    │ date         │         │
│ mascot      │    │ year         │    ┌─────────────┐
│ school_type │    │ location     │    │    match    │
│ school_url  │    └──────────────┘    │             │
└─────────────┘                       │ match_id    │
                                      │ round       │
┌─────────────┐                       │ round_order │
│participant_ │                       │bracket_order│
│   match     │                       │tournament_id│
│             │                       │ result_type │
│ match_id    │◄─────────────────────►│ fall_time   │
│participant_id│                      │ tech_time   │
│ is_winner   │                       │ winner_id   │
│ score       │                       └─────────────┘
│next_match_id│                       
└─────────────┘                       
```

## Migration Status

As of the current date, the database migration is in progress:
- ✅ **person** table: Fully populated with 10,000+ records
- 🔄 **role** table: Migration in progress
- 🔄 **participant** table: Migration in progress  
- 🔄 **school** table: Migration in progress
- 🔄 **tournament** table: Migration in progress
- 🔄 **match** table: Migration in progress
- 🔄 **participant_match** table: Migration in progress

## Current API Status

During migration, the following endpoints are available:
- `/api/search/people` - Simple person search (working)
- `/api/wrestlers/profile-simple/{id}` - Basic wrestler profiles (working)
- `/api/search/wrestlers` - Full search with hints (ready for post-migration)
- `/api/search/test-db` - Database connection test

---

**Last Updated:** July 19, 2025  
**Schema Version:** 1.0  
**Environment:** Supabase PostgreSQL
**Migration Status:** In Progress

# CI/CD and Deployment Guide

This document explains the new CI/CD pipeline and deployment process for the Louden Swain wrestling platform.

## Overview

The project now uses GitHub Actions for continuous integration and deployment, with multiple environments managed through Vercel.

## Architecture

### Environments

1. **Production** (`main` branch) - `https://louden-swain.vercel.app`
2. **Test/Staging** (`test` branch) - Preview deployment URL
3. **Preview** (feature branches/PRs) - Temporary preview URLs

### CI/CD Workflows

#### 1. Continuous Integration (`.github/workflows/ci.yml`)

Runs on:
- Push to `main`, `test`, or development branches
- Pull requests to `main` or `test` branches

**Quality Gates:**
- Frontend linting (`npm run lint`)
- Frontend type checking (`npm run type-check`)
- Frontend build verification
- Backend linting (`flake8`)
- Backend code formatting check (`black --check`)
- Backend import sorting check (`isort --check-only`)
- Backend tests (`pytest`)
- Security scanning (npm audit, Python safety check)

#### 2. Production Deployment (`.github/workflows/deploy-production.yml`)

Runs on:
- Push to `main` branch
- Manual trigger

**Process:**
1. Runs all quality gates
2. Deploys to Vercel production environment
3. Updates deployment status

#### 3. Test Environment Deployment (`.github/workflows/deploy-test.yml`)

Runs on:
- Push to `test` branch
- Manual trigger

**Process:**
1. Runs quality gates
2. Deploys to Vercel test environment
3. Comments deployment URL on commits

#### 4. Preview Deployments (`.github/workflows/deploy-preview.yml`)

Runs on:
- Pull requests to `main` or `test` branches

**Process:**
1. Runs quality gates (frontend only for speed)
2. Creates preview deployment
3. Comments preview URL on PR

## Required Secrets

The following secrets need to be configured in GitHub repository settings:

### Vercel Secrets
- `VERCEL_TOKEN` - Vercel CLI token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID` - Vercel project ID for production
- `VERCEL_PROJECT_ID_TEST` - Vercel project ID for test environment

### Getting Vercel Secrets

1. **VERCEL_TOKEN**: Generate at [Vercel Dashboard](https://vercel.com/account/tokens)
2. **VERCEL_ORG_ID & VERCEL_PROJECT_ID**: Run `vercel link` in your project root

## Local Development Scripts

New package.json scripts for testing the complete pipeline locally:

```bash
# Frontend quality checks
npm run test:frontend

# Backend quality checks (requires Python dependencies)
npm run test:backend

# Run all quality checks
npm run test

# Format backend code
npm run format:backend

# Setup backend dependencies
npm run setup:backend
```

## Vercel Configuration

The `vercel.json` file configures:
- Frontend build settings (Next.js)
- Backend API routing (Python FastAPI)
- Security headers
- Environment variables

## Branch Strategy

### Main Branch (`main`)
- Production-ready code only
- Auto-deploys to production
- All quality gates must pass
- Protected branch (recommended)

### Test Branch (`test`)
- Staging/QA environment
- Auto-deploys to test environment
- Used for pre-production testing

### Feature Branches
- Development work
- Create preview deployments via PRs
- Must pass quality gates to merge

## Deployment Process

### Production Deployment
1. Create PR to `main` branch
2. Ensure all CI checks pass
3. Get approval and merge
4. Automatic deployment to production

### Test Deployment
1. Push to `test` branch (or create PR to `test`)
2. Automatic deployment to test environment
3. Test features in staging

### Preview Deployment
1. Create PR to `main` or `test`
2. Automatic preview deployment created
3. Review changes using preview URL

## Environment Variables

Set environment-specific variables in:
- Vercel dashboard for production/test environments
- `.env.local` for local development
- GitHub secrets for CI/CD workflows

## Monitoring and Rollback

### Monitoring
- Check deployment status in Vercel dashboard
- Monitor GitHub Actions workflow results
- Review deployment comments on PRs/commits

### Rollback
1. **Quick rollback**: Revert commit in `main` branch
2. **Vercel rollback**: Use Vercel dashboard to rollback to previous deployment
3. **Manual rollback**: Deploy specific commit using workflow_dispatch

## Security Features

- All deployments require passing quality gates
- Security scanning with npm audit and Python safety
- Environment separation prevents test data in production
- Secure secrets management through GitHub Actions

## Troubleshooting

### Common Issues

1. **Quality gates failing**: Check linting and test errors in CI logs
2. **Deployment failing**: Verify Vercel secrets are correctly configured
3. **Build errors**: Ensure dependencies are properly specified in package.json/requirements.txt

### Support Commands

```bash
# Test frontend locally
cd frontend && npm run lint && npm run type-check && npm run build

# Test backend locally
cd backend && flake8 && black --check . && python -m pytest

# Manual Vercel deployment (with CLI installed)
vercel --prod  # Production
vercel         # Preview
```
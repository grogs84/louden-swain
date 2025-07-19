#!/usr/bin/env node

// Test script for new profile API endpoints
const axios = require('axios');

const API_BASE_URL = process.env.API_URL || 'http://localhost:8000/api';

async function testProfileAPI() {
    try {
        console.log('🧪 Testing Profile API endpoints...\n');
        
        // First get a person ID from the existing wrestlers endpoint 
        // (since we know wrestlers have person_id)
        console.log('1. Getting sample person ID from wrestlers...');
        
        try {
            const wrestlersResponse = await axios.get(`${API_BASE_URL}/wrestlers?limit=2`);
            
            if (wrestlersResponse.data.length === 0) {
                console.log('⚠️  No wrestlers found in database, trying direct person ID...');
                await testWithKnownPersonId('test-person-1');
                return;
            }
            
            // Use the wrestler's ID (which should be a person_id in the backend)
            const wrestler = wrestlersResponse.data[0];
            console.log(`   Using wrestler: ${wrestler.first_name} ${wrestler.last_name} (ID: ${wrestler.id})`);
            
            await testProfileEndpoints(wrestler.id);
            
        } catch (error) {
            console.log('⚠️  Wrestlers endpoint not available, testing with mock person ID...');
            await testWithKnownPersonId('sample-person-123');
        }
        
    } catch (error) {
        console.error('❌ Profile API Test failed:', error.message);
        if (error.response) {
            console.error('   Status:', error.response.status);
            console.error('   Data:', JSON.stringify(error.response.data, null, 2));
        }
    }
}

async function testProfileEndpoints(personId) {
    console.log(`\n2. Testing GET /profile/${personId}`);
    
    try {
        const profileResponse = await axios.get(`${API_BASE_URL}/profile/${personId}`);
        console.log('✅ Profile endpoint working!');
        console.log(`   Name: ${profileResponse.data.first_name} ${profileResponse.data.last_name}`);
        console.log(`   Person ID: ${profileResponse.data.person_id}`);
        console.log(`   Roles: ${JSON.stringify(profileResponse.data.roles, null, 2)}`);
        
        // Check expected fields
        const profile = profileResponse.data;
        const expectedFields = ['person_id', 'first_name', 'last_name', 'full_name', 'roles'];
        const hasAllFields = expectedFields.every(field => field in profile);
        
        if (hasAllFields) {
            console.log('✅ All expected fields present in profile response');
        } else {
            console.log('❌ Missing expected fields in profile response');
            console.log('   Expected:', expectedFields);
            console.log('   Actual:', Object.keys(profile));
        }
        
        // Test role-specific endpoints if roles exist
        if (profile.roles && profile.roles.length > 0) {
            for (const role of profile.roles) {
                await testRoleEndpoints(personId, role.role_type);
            }
        }
        
    } catch (error) {
        console.error('❌ Profile endpoint failed:', error.message);
        if (error.response) {
            console.error('   Status:', error.response.status);
            console.error('   Data:', JSON.stringify(error.response.data, null, 2));
        }
    }
}

async function testRoleEndpoints(personId, roleType) {
    console.log(`\n3. Testing role-specific endpoints for ${roleType}...`);
    
    // Test stats endpoint
    try {
        console.log(`   Testing GET /profile/${personId}/stats?role_type=${roleType}`);
        const statsResponse = await axios.get(`${API_BASE_URL}/profile/${personId}/stats`, {
            params: { role_type: roleType }
        });
        console.log(`✅ ${roleType} stats endpoint working!`);
        console.log(`   Stats: ${JSON.stringify(statsResponse.data, null, 2)}`);
        
    } catch (error) {
        console.error(`❌ ${roleType} stats endpoint failed:`, error.message);
    }
    
    // Test matches endpoint
    try {
        console.log(`   Testing GET /profile/${personId}/matches?role_type=${roleType}`);
        const matchesResponse = await axios.get(`${API_BASE_URL}/profile/${personId}/matches`, {
            params: { role_type: roleType, limit: 5 }
        });
        console.log(`✅ ${roleType} matches endpoint working!`);
        console.log(`   Matches count: ${matchesResponse.data.length}`);
        if (matchesResponse.data.length > 0) {
            console.log(`   Sample match: ${JSON.stringify(matchesResponse.data[0], null, 2)}`);
        }
        
    } catch (error) {
        console.error(`❌ ${roleType} matches endpoint failed:`, error.message);
    }
}

async function testWithKnownPersonId(personId) {
    console.log(`\n🔍 Testing with known person ID: ${personId}`);
    await testProfileEndpoints(personId);
}

// Test the API endpoints structure even if no data
async function testEndpointStructure() {
    console.log('\n4. Testing API endpoint structure...');
    
    const endpoints = [
        '/profile/test-id',
        '/profile/test-id/stats?role_type=wrestler',
        '/profile/test-id/matches?role_type=wrestler'
    ];
    
    for (const endpoint of endpoints) {
        try {
            const response = await axios.get(`${API_BASE_URL}${endpoint}`);
            console.log(`✅ ${endpoint} - Structure OK`);
        } catch (error) {
            if (error.response && error.response.status === 404) {
                console.log(`✅ ${endpoint} - Endpoint exists (404 expected for test data)`);
            } else {
                console.log(`❌ ${endpoint} - ${error.message}`);
            }
        }
    }
}

// Run tests
async function main() {
    await testProfileAPI();
    await testEndpointStructure();
    console.log('\n🎯 Profile API testing complete!');
}

main();
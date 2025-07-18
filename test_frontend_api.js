#!/usr/bin/env node

// Test script to simulate frontend API calls
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8001/api';

async function testWrestlerAPI() {
    try {
        console.log('🧪 Testing Frontend API calls...\n');
        
        // Test 1: Get wrestler list
        console.log('1. Testing GET /wrestlers');
        const wrestlersResponse = await axios.get(`${API_BASE_URL}/wrestlers?limit=5`);
        console.log(`✅ Wrestlers: ${wrestlersResponse.data.length} results`);
        
        if (wrestlersResponse.data.length > 0) {
            const wrestler = wrestlersResponse.data[1]; // Get second wrestler (id=2)
            console.log(`   Sample wrestler: ${wrestler.first_name} ${wrestler.last_name} (ID: ${wrestler.id})`);
            
            // Test 2: Get wrestler detail
            console.log(`\n2. Testing GET /wrestlers/${wrestler.id}`);
            const wrestlerResponse = await axios.get(`${API_BASE_URL}/wrestlers/${wrestler.id}`);
            console.log(`✅ Wrestler detail: ${wrestlerResponse.data.first_name} ${wrestlerResponse.data.last_name}`);
            
            // Test 3: Get wrestler stats
            console.log(`\n3. Testing GET /wrestlers/${wrestler.id}/stats`);
            const statsResponse = await axios.get(`${API_BASE_URL}/wrestlers/${wrestler.id}/stats`);
            console.log(`✅ Stats: ${JSON.stringify(statsResponse.data, null, 2)}`);
            
            // Check if stats has the expected fields
            const expectedFields = ['wins', 'losses', 'win_percentage', 'pins', 'tech_falls', 'major_decisions'];
            const hasAllFields = expectedFields.every(field => field in statsResponse.data);
            
            if (hasAllFields) {
                console.log('✅ All expected fields present in stats response');
            } else {
                console.log('❌ Missing expected fields in stats response');
                console.log('   Expected:', expectedFields);
                console.log('   Actual:', Object.keys(statsResponse.data));
            }
        }
        
    } catch (error) {
        console.error('❌ API Test failed:', error.message);
        if (error.response) {
            console.error('   Status:', error.response.status);
            console.error('   Data:', error.response.data);
        }
    }
}

testWrestlerAPI();

# Wrestling Data Hub - Team Demo Script

## 🏆 NCAA D1 Wrestling Championship Data Platform

### **Demo Overview (5 minutes)**

**What we built:**
- Modern React frontend with Material-UI
- FastAPI backend with PostgreSQL database
- Full CRUD operations for wrestlers, schools, coaches
- Advanced search functionality
- Tournament bracket visualization (placeholder)

---

### **Live Demo Flow**

#### 1. **Home Page** (30 seconds)
- Clean, professional landing page
- Navigation to different sections
- Quick action cards for main features

#### 2. **Search Functionality** (2 minutes)
**Try these searches:**
- Search "Taylor" → Shows David Taylor (Penn State wrestler)
- Search "Penn State" → Shows school and associated wrestlers  
- Search by weight class: Filter wrestlers by 165 lbs
- Search by conference: Filter schools by "Big Ten"

**Show off:**
- Real-time search results
- Tabbed interface (All/Wrestlers/Schools/Coaches)
- Filter options for advanced search

#### 3. **Wrestler Profiles** (1 minute)
- Click on "David Taylor" from search results
- Shows detailed wrestler information:
  - Name, weight class, year, hometown
  - School affiliation
  - Placeholder for statistics (wins/losses)

#### 4. **School Pages** (1 minute)
- Navigate to Penn State from wrestler profile
- Shows school information:
  - Conference, location
  - Associated wrestlers and coaches
  - Program statistics

#### 5. **API Documentation** (30 seconds)
- Show FastAPI auto-generated docs at `/docs`
- Demonstrate API endpoints
- Show real data responses

---

### **Technical Highlights**

**Backend (FastAPI + PostgreSQL):**
✅ Direct database connection (no more Supabase REST API)  
✅ SQLAlchemy ORM with async support  
✅ Full CRUD operations for all entities  
✅ Advanced search with PostgreSQL ILIKE queries  
✅ Automatic API documentation  
✅ Sample data populated and tested  

**Frontend (React + Material-UI):**
✅ Modern, responsive design  
✅ React Router for navigation  
✅ React Query for data fetching  
✅ Material-UI components for professional look  
✅ Search with real-time filtering  
✅ Error handling and loading states  

**Integration:**
✅ Frontend ↔ Backend API communication working  
✅ Environment configuration  
✅ CORS properly configured  
✅ Both servers running simultaneously  

---

### **Current Data**

**Sample wrestlers:**
- David Taylor (Penn State, 165 lbs)
- Kyle Dake (Penn State, 174 lbs) 
- Bo Nickal (Penn State, 184 lbs)
- Carter Starocci (Penn State, 174 lbs)
- Spencer Lee (Iowa, 125 lbs)

**Sample schools:**
- Penn State University (Big Ten)
- University of Iowa (Big Ten)
- Oklahoma State University (Big 12)
- Ohio State University (Big Ten)
- Iowa State University (Big 12)

---

### **Next Steps & Future Features**

**Immediate priorities:**
- [ ] Deploy to cloud (Vercel + Railway)
- [ ] Add more sample data
- [ ] Implement tournament bracket visualization
- [ ] Add authentication system

**Future enhancements:**
- [ ] Match result tracking
- [ ] Statistical analysis and charts
- [ ] Real-time tournament updates
- [ ] Mobile app development
- [ ] Data import from external sources

---

### **Questions to Ask Team**

1. **Data Sources:** What additional wrestling data should we integrate?
2. **Features:** Which features are highest priority for users?
3. **Design:** Any UI/UX feedback or suggestions?
4. **Deployment:** Should we proceed with cloud deployment?
5. **Timeline:** What's the target launch date?

---

**Live URLs (after deployment):**
- Frontend: `https://wrestling-hub.vercel.app` 
- Backend API: `https://wrestling-api.railway.app`
- API Docs: `https://wrestling-api.railway.app/docs`

# 🏆 NCAA Wrestling Championship Data App - LIVE DEMO

## 🚀 **Live URLs**

### **Backend API (Railway)**
- **URL**: https://wrestling-data-hub-production.up.railway.app
- **API Documentation**: https://wrestling-data-hub-production.up.railway.app/docs
- **Health Check**: https://wrestling-data-hub-production.up.railway.app/health

### **Frontend (To be deployed)**
- **Status**: Ready for deployment to Vercel
- **Environment**: Configured to use Railway backend

---

## 📊 **API Endpoints Available**

| Endpoint | Description | Example |
|----------|-------------|---------|
| `/api/wrestlers` | Get all wrestlers | [View](https://wrestling-data-hub-production.up.railway.app/api/wrestlers) |
| `/api/wrestlers/{id}` | Get wrestler by ID | [View](https://wrestling-data-hub-production.up.railway.app/api/wrestlers/1) |
| `/api/schools` | Get all schools | [View](https://wrestling-data-hub-production.up.railway.app/api/schools) |
| `/api/schools/{id}` | Get school by ID | [View](https://wrestling-data-hub-production.up.railway.app/api/schools/1) |
| `/api/coaches` | Get all coaches | [View](https://wrestling-data-hub-production.up.railway.app/api/coaches) |
| `/api/tournaments` | Get all tournaments | [View](https://wrestling-data-hub-production.up.railway.app/api/tournaments) |
| `/api/brackets/{tournament_id}` | Get tournament brackets | [View](https://wrestling-data-hub-production.up.railway.app/api/brackets/1) |
| `/api/search` | Search functionality | Try: `?q=iowa&type=school` |

---

## 🔧 **Technical Stack**

### **Backend (✅ DEPLOYED)**
- **FastAPI** - Python web framework
- **PostgreSQL** - Database (Supabase)
- **SQLAlchemy** - ORM with async support
- **Railway** - Hosting platform

### **Frontend (📋 READY FOR DEPLOYMENT)**
- **React** - Frontend framework
- **Material-UI** - UI components
- **React Router** - Navigation
- **Axios** - API client

---

## 🎯 **Features Implemented**

✅ **Wrestler Management**
- Detailed wrestler profiles
- Statistics and records
- Weight class information

✅ **School Data**
- School profiles and stats
- Coach information
- Team performance metrics

✅ **Tournament System**
- Tournament brackets
- Match results
- Championship tracking

✅ **Search Functionality**
- Multi-type search (wrestlers, schools, coaches)
- Real-time filtering
- Quick navigation

✅ **Data Visualization**
- Performance charts
- Weight class distributions
- Tournament brackets

---

## 🚀 **Quick Start for Team**

### **1. Test the API**
```bash
# Check if backend is running
curl https://wrestling-data-hub-production.up.railway.app/health

# Get all wrestlers
curl https://wrestling-data-hub-production.up.railway.app/api/wrestlers

# Get specific wrestler
curl https://wrestling-data-hub-production.up.railway.app/api/wrestlers/1
```

### **2. Frontend Deployment Options**

#### **Option A: Vercel (Recommended)**
1. Fork/clone the repository
2. Connect to Vercel GitHub integration
3. Set environment variable: `REACT_APP_API_URL=https://wrestling-data-hub-production.up.railway.app`
4. Deploy automatically

#### **Option B: Netlify**
1. Build the frontend: `npm run build`
2. Deploy the `build` folder to Netlify
3. Configure environment variables

#### **Option C: Local Development**
```bash
git clone <your-repo>
cd frontend
npm install
npm start
```

---

## 📈 **Sample Data Included**

- **10+ Wrestlers** with detailed stats
- **5+ Schools** with performance data
- **3+ Coaches** with records
- **2+ Tournaments** with brackets
- **Multiple Weight Classes** (125-285 lbs)

---

## 🛠 **Development Commands**

```bash
# Backend (Local)
cd backend
python -m uvicorn app.main:app --reload

# Frontend (Local)
cd frontend
npm start

# Database Setup
cd backend
python recreate_database.py
```

---

## 🔐 **Environment Variables**

### **Backend (.env)**
```env
DATABASE_URL=postgresql://[user]:[password]@[host]/[db]
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[your_anon_key]
```

### **Frontend (.env)**
```env
REACT_APP_API_URL=https://wrestling-data-hub-production.up.railway.app
```

---

## 📞 **Support & Next Steps**

### **Immediate Actions**
1. ✅ Backend deployed and running
2. 🔄 Deploy frontend to Vercel/Netlify
3. 📝 Test all functionality
4. 🎨 Customize branding/styling

### **Future Enhancements**
- User authentication
- Real-time updates
- Advanced analytics
- Mobile responsiveness
- PDF report generation

### **Contact**
- **Repository**: [Your GitHub Repository]
- **Backend**: https://wrestling-data-hub-production.up.railway.app
- **Documentation**: Available in `/docs` endpoint

---

**🏆 Ready to demo your NCAA Wrestling Championship data app!**

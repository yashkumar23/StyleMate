# STYLEMATE - AI Fashion Assistant

## 🎯 Project Overview

STYLEMATE is a modern AI-powered fashion assistant web application that provides personalized style recommendations based on user's physical attributes like skin tone, body measurements, and body type. The application features a sleek, desktop-optimized design with robust user authentication and body analysis capabilities.

## ✨ Features Implemented

### 🎨 **Design & UI**
- **Simple & Sleek Design**: Clean, modern interface inspired by contemporary fashion apps
- **Desktop-Optimized**: Split-screen layouts perfect for web browsers
- **Teal Color Scheme**: Professional #008080 teal with white and grey accents
- **Hanger Icon Logo**: Custom logo with clothing hanger icon
- **Responsive Design**: Adapts to different screen sizes

### 🔐 **Authentication System**
- **User Registration**: Complete signup flow with validation
- **Secure Login**: Password hashing with Werkzeug
- **Database Integration**: SQLite database for user storage
- **Session Management**: Flask sessions with remember me functionality
- **Skip Option**: Direct dashboard access without login
- **Password Strength Checker**: Real-time password validation

### 📸 **Body Analysis System**
- **Image Upload**: Front and side-view photo upload with drag & drop
- **File Validation**: Size and format validation (JPG, PNG, WebP up to 10MB)
- **Height Input**: Interactive height input with slider (100-250 cm)
- **Progress Tracking**: Real-time upload and analysis progress
- **AI Integration Ready**: Backend API prepared for AI model integration

### 📱 **Pages Implemented**
1. **Homepage**: Welcome screen with call-to-action
2. **Signup Page**: User registration with form validation
3. **Signin Page**: Authentication with Skip button
4. **Dashboard**: User dashboard with analysis access
5. **Body Analysis**: Image upload and measurement input page

## 🛠 **Technical Stack**

### Backend
- **Flask**: Python web framework
- **SQLAlchemy**: Database ORM
- **Werkzeug**: Password hashing and security
- **Flask-CORS**: Cross-origin resource sharing
- **SQLite**: Database storage

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with animations
- **JavaScript**: Form validation and interactions
- **Responsive Design**: Mobile-first approach

## 🚀 **Installation & Setup**

### Prerequisites
- Python 3.11+
- Virtual environment support

### Quick Start
```bash
# Extract the project
tar -xzf stylemate_with_analysis.tar.gz
cd stylemate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask flask-sqlalchemy flask-cors werkzeug

# Run the application
cd src
python main.py
```

### Access the Application
- **Homepage**: http://127.0.0.1:5000
- **Signup**: http://127.0.0.1:5000/signup.html
- **Signin**: http://127.0.0.1:5000/signin.html
- **Dashboard**: http://127.0.0.1:5000/dashboard.html
- **Body Analysis**: http://127.0.0.1:5000/analysis.html

## 🔄 **User Flow**

### Registration & Authentication Flow
1. User visits homepage
2. Clicks "Get Started" → Redirects to signup
3. Fills registration form with validation
4. Account created → Redirects to signin
5. User signs in → Redirects to dashboard
6. **Alternative**: Skip signin → Direct dashboard access

### Body Analysis Flow
1. User accesses dashboard
2. Clicks "Start Body Analysis"
3. Uploads front and side-view photos
4. Enters height measurement
5. Clicks "Analyze My Style"
6. System processes images and data
7. Results displayed (ready for AI integration)

## 🗄️ **Database Schema**

### Users Table
```sql
- id (Primary Key)
- first_name (String, 50 chars)
- last_name (String, 50 chars)
- email (String, 120 chars, Unique)
- password_hash (String, 255 chars)
- created_at (DateTime)
- updated_at (DateTime)
- is_active (Boolean)
```

## 🔒 **Security Features**

- **Password Hashing**: Werkzeug secure password hashing
- **Input Validation**: Client and server-side validation
- **File Upload Security**: Type and size validation
- **CSRF Protection**: Flask session security
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **XSS Protection**: Proper input sanitization

## 📋 **API Endpoints**

### Authentication Routes
- `POST /api/signup` - User registration
- `POST /api/signin` - User login
- `POST /api/logout` - User logout
- `GET /api/user` - Get current user
- `POST /api/check-email` - Check email availability

### Body Analysis Routes
- `POST /api/analyze` - Submit body analysis request
- `GET /api/analysis/<id>` - Get analysis results
- `GET /api/upload-progress` - Get upload progress

### Static Routes
- `GET /` - Homepage
- `GET /signup.html` - Signup page
- `GET /signin.html` - Signin page
- `GET /dashboard.html` - Dashboard page
- `GET /analysis.html` - Body analysis page

## 🧪 **Testing**

### Demo Credentials
- **Email**: demo@stylemate.com
- **Password**: demo123

### Test User Created
- **Email**: john.doe@test.com
- **Password**: TestPass123!

### Body Analysis Testing
1. Navigate to `/analysis.html`
2. Upload test images (JPG/PNG format)
3. Set height value (100-250 cm)
4. Click "Analyze My Style"
5. Verify upload and processing

## 🎯 **AI Integration Ready**

### Backend API Structure
The `/api/analyze` endpoint is prepared for AI model integration:

```python
# Current mock response structure
analysis_result = {
    'body_type': 'Athletic',
    'skin_tone': 'Medium',
    'recommended_styles': [...],
    'color_palette': [...],
    'confidence_score': 0.92
}
```

### File Storage
- Uploaded images saved to `uploads/` directory
- Unique filenames with timestamps
- Ready for AI model processing

## 🎨 **Design Features**

### Body Analysis Page
- **Split-screen Layout**: Branding on left, form on right
- **Step-by-step Guide**: Visual progress indicators
- **Drag & Drop Upload**: Intuitive file upload areas
- **Interactive Height Input**: Slider with real-time sync
- **Progress Animation**: Loading states and feedback
- **Responsive Design**: Works on all screen sizes

### Visual Elements
- **Animated Backgrounds**: Subtle grid patterns
- **Hover Effects**: Interactive button states
- **Loading Spinners**: Professional loading indicators
- **Color-coded Validation**: Visual feedback for inputs
- **Smooth Transitions**: CSS animations throughout

## 🚀 **Future Enhancements**

### Planned Features
- AI model integration for style recommendations
- Results page with detailed analysis
- User profile management
- Style history and favorites
- Social sharing features
- Mobile app version

### Technical Improvements
- Production database (PostgreSQL)
- Email verification system
- Advanced file processing
- Real-time analysis progress
- Comprehensive testing suite
- Docker containerization

## 📁 **Project Structure**

```
stylemate/
├── src/
│   ├── main.py                 # Flask application entry point
│   ├── models/
│   │   └── user.py            # User model and database setup
│   ├── routes/
│   │   ├── auth.py            # Authentication routes
│   │   └── analysis.py        # Body analysis routes
│   ├── static/
│   │   ├── index.html         # Homepage
│   │   ├── signup.html        # Signup page
│   │   ├── signin.html        # Signin page
│   │   ├── analysis.html      # Body analysis page
│   │   └── hanger-icon.png    # Logo icon
│   └── uploads/               # Image upload directory
├── venv/                      # Virtual environment (excluded)
└── README.md                  # This file
```

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## 📄 **License**

This project is proprietary software for STYLEMATE fashion assistant application.

## 📞 **Support**

For technical support or questions about the implementation, please refer to the code comments and documentation within the source files.

---

**STYLEMATE** - Your Personalized Fashion Assistant
*Powered by AI, Designed for Style*

### 🎉 **Ready for AI Integration!**
The body analysis system is fully implemented and ready for your AI models. Simply integrate your fashion recommendation algorithms with the `/api/analyze` endpoint to provide personalized style suggestions based on uploaded photos and measurements.


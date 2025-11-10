# 🎬 Movie Tracker

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-Cloud-brightgreen.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)
![Deployment](https://img.shields.io/badge/Deployed%20on-Render-purple.svg)

A full-stack web application that allows users to search, track, and manage movies in a simple and interactive way.

🔗 **[Live Demo](https://movies-tracker-pop1.onrender.com/)**

---

## 🌟 Features

- **🔍 Search for movies**: Quickly find movies by title using the integrated TMDB API
- **📋 Watchlist management**: Add movies to your personal watchlist to keep track of what you want to watch
- **🎨 User-friendly interface**: Clean and responsive UI built with HTML, CSS, and JavaScript
- **💾 Persistent data storage**: All watchlists and user interactions are stored in MongoDB
- **🚀 Deployment & uptime**: Hosted on Render and kept active with Uptime Robot to ensure 24/7 availability

---

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **MongoDB** - Cloud-hosted NoSQL database
- **Gunicorn** - WSGI HTTP server

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling
- **JavaScript** - Client-side functionality

### APIs & Services
- **TMDB API** - Movie data and information
- **Render** - Deployment platform
- **Uptime Robot** - Monitoring and uptime management

### DevOps
- **Docker** - Containerization
- **Python-dotenv** - Environment variable management
- **bcrypt** - Password hashing

---

## 📁 Project Structure
```
movies/
│
├── app/
│   ├── static/              # CSS, JS
│   ├── templates/           # HTML templates
│   ├── __init__.py
│   ├── routes.py            # Flask routes and endpoints
│   ├── tmdb_api.py          # Handles movie API requests
│   └── helper_functions.py  # Utility functions
│
├── Dockerfile
├── docker-compose.yml
├── main.py
├── requirements.txt
├── .env
└── .gitignore
```

---

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/TTpythonify/movies_tracker.git
cd movies
```

### 2. Create and activate a virtual environment
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory with the following:
```env
MONGODB_URI=your_mongodb_connection_string
TMDB_API_KEY=your_tmdb_api_key
SECRET_KEY=your_secret_key
```

### 5. Run the app
```bash
python main.py
```

### 6. Visit the app
Open your browser at `http://localhost:5000`

---

## 🐳 Using Docker

### Build and run the container:
```bash
docker build -t movie-tracker .
docker run -p 5000:5000 movie-tracker
```

### Or use Docker Compose:
```bash
docker-compose up
```

---

## 📌 Deployment

The app is deployed on **Render**: [https://movies-tracker-pop1.onrender.com/](https://movies-tracker-pop1.onrender.com/)

**Uptime Robot** is used to keep the app active and prevent sleep downtime.

### Deployment Steps:
1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Deploy using the provided `Dockerfile` or build command
4. Configure Uptime Robot to ping your app URL every 5 minutes

---

## 📚 Notes

- The app is designed for multiple concurrent users
- Data is securely stored in MongoDB
- Movie data is fetched in real-time from the TMDB API
- Passwords are hashed using bcrypt for security

---

## 💡 Future Improvements

- [ ] User authentication and profiles
- [ ] Movie ratings and reviews
- [ ] Social sharing of watchlists
- [ ] Advanced search filters by genre, year, and rating
- [ ] Recommendation engine based on watchlist
- [ ] Dark mode toggle
- [ ] Email notifications for new releases

---

## 📝 API Reference

### TMDB API
This project uses [The Movie Database (TMDB) API](https://www.themoviedb.org/documentation/api) to fetch movie data.

To get your own API key:
1. Create an account at [TMDB](https://www.themoviedb.org/)
2. Go to Settings → API
3. Request an API key
4. Add it to your `.env` file

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🙏 Credits & Acknowledgments

- **Flask**: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- **MongoDB**: [https://www.mongodb.com/](https://www.mongodb.com/)
- **TMDB API**: [https://www.themoviedb.org/documentation/api](https://www.themoviedb.org/documentation/api)
- **Render**: [https://render.com/](https://render.com/)
- **Docker**: [https://www.docker.com/](https://www.docker.com/)

---

⭐ **Star this repo if you found it helpful!**

🍿 **Check out the app and start discovering your next favorite movie today!**

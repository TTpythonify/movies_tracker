// Get modal elements
const movieModal = document.getElementById('movieModal');
const watchlistModal = document.getElementById('watchlistModal');
const watchedModal = document.getElementById('watchedModal');
const notificationsModal = document.getElementById('notificationsModal');

// Function to open movie details modal
function openMovieModal(movieId) {
    movieModal.style.display = 'block';

    fetch(`/movie/${movieId}`)
        .then(response => response.json())
        .then(data => {
            displayMovieDetails(data);
        })
        .catch(error => {
            document.getElementById('modalBody').innerHTML = '<p>Error loading movie details.</p>';
        });
}

// Function to display movie details in modal
function displayMovieDetails(movie) {
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <div class="modal-movie-details">
            ${movie.backdrop_url ? `<img src="${movie.backdrop_url}" alt="${movie.title}" class="modal-backdrop">` : ''}
            <div class="modal-info-container">
                ${movie.poster_url ? `<img src="${movie.poster_url}" alt="${movie.title}" class="modal-poster">` : '<div class="placeholder-poster">No Image</div>'}
                <div class="modal-text-info">
                    <h2>${movie.title}</h2>
                    <p class="modal-tagline">${movie.tagline || ''}</p>
                    <p><strong>Release Date:</strong> ${movie.release_date || 'N/A'}</p>
                    <p><strong>Runtime:</strong> ${movie.runtime ? movie.runtime + ' minutes' : 'N/A'}</p>
                    <p class="modal-rating">⭐ ${movie.vote_average || 0} / 10 (${movie.vote_count || 0} votes)</p>
                    <p class="modal-genres"><strong>Genres:</strong> ${movie.genres || 'N/A'}</p>
                    <p class="modal-overview"><strong>Overview:</strong><br>${movie.overview || 'No overview available.'}</p>

                    <div class="modal-actions">
                        <button class="btn-watchlist" onclick="addToWatchlist(${movie.id})">Add to Watch Later</button>
                        <button class="btn-watched" onclick="addToWatched(${movie.id})">Mark as Watched</button>
                    </div>
                </div>
            </div>

            <div class="reviews-section">
                <h3>User Reviews</h3>
                <div class="add-review-form">
                    <textarea id="reviewText" placeholder="Write your review..." rows="3"></textarea>
                    <button class="btn-submit-review" onclick="submitReview(${movie.id})">Submit Review</button>
                </div>
                <div id="reviewsList" class="reviews-list">
                    ${movie.reviews && movie.reviews.length > 0
                        ? movie.reviews.map(r => `
                            <div class="review-item">
                                <div class="review-header">
                                    <strong>${r.username}</strong>
                                    <span class="review-date">${r.date}</span>
                                </div>
                                <p class="review-text">${r.reviewText}</p>
                            </div>
                        `).join('')
                        : '<p class="no-reviews">No reviews yet. Be the first!</p>'
                    }
                </div>
            </div>
        </div>
    `;
}

// Function to open watchlist modal
function openWatchlistModal() {
    watchlistModal.style.display = 'block';
    document.getElementById('watchlistBody').innerHTML = '<div class="loading">Loading...</div>';

    fetch('/get_watchlist')
        .then(response => response.json())
        .then(data => {
            displayListModal(data.movies, 'watchlistBody', 'Watch Later List', 'Your watch later list is empty. Start adding movies!');
        })
        .catch(error => {
            document.getElementById('watchlistBody').innerHTML = '<p>Error loading watchlist.</p>';
        });
}


// Function to open watched modal
function openWatchedModal() {
    watchedModal.style.display = 'block';
    document.getElementById('watchedBody').innerHTML = '<div class="loading">Loading...</div>';

    fetch('/get_watched')
        .then(response => response.json())
        .then(data => {
            displayListModal(data.movies, 'watchedBody', 'Watched Movies', 'You haven\'t marked any movies as watched yet.');
        })
        .catch(error => {
            document.getElementById('watchedBody').innerHTML = '<p>Error loading watched movies.</p>';
        });
}


// Function to open notifications modal
function openNotificationsModal() {
    notificationsModal.style.display = 'block';
    const notificationsBody = document.getElementById('notificationsBody');
    notificationsBody.innerHTML = '<div class="loading">Loading...</div>';

    fetch('/get_notifications')  // Make sure you have a Flask route returning notifications
        .then(response => response.json())
        .then(data => {
            displayNotifications(data.notifications);
        })
        .catch(error => {
            notificationsBody.innerHTML = '<p>Error loading notifications.</p>';
            console.error(error);
        });
}


function displayNotifications(notifications) {
    const body = document.getElementById('notificationsBody');
    
    if (notifications && notifications.length > 0) {
        body.innerHTML = `
            <div class="list-modal-content">
                <h2>Notifications</h2>
                <ul class="notifications-list">
                    ${notifications.map(n => `
                        <li>
                            <strong>${n.reviewer}</strong> commented on movie ID ${n.movie_id}:
                            <p>${n.text}</p>
                            <span class="notification-date">${n.date}</span>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    } else {
        body.innerHTML = `
            <div class="list-modal-content">
                <h2>Notifications</h2>
                <p>You have no notifications yet.</p>
            </div>
        `;
    }
}

// Close notifications modal
function closeNotificationsModal() {
    notificationsModal.style.display = 'none';
}

// Optional: Close modal when clicking outside
window.onclick = e => {
    if (e.target == notificationsModal) closeNotificationsModal();
}


// Function to display list in modal
function displayListModal(movies, bodyId, title, emptyMessage) {
    const body = document.getElementById(bodyId);
    
    if (movies && movies.length > 0) {
        body.innerHTML = `
            <div class="list-modal-content">
                <h2>${title}</h2>
                <div class="list-modal-grid">
                    ${movies.map(movie => `
                        <div class="list-movie-card" onclick="openMovieModal(${movie.id})">
                            ${movie.poster_url 
                                ? `<img src="${movie.poster_url}" alt="${movie.title}">` 
                                : '<div class="placeholder-poster">No Image</div>'}
                            <div class="list-movie-info">
                                <h3>${movie.title}</h3>
                                <p class="release-date">${movie.release_date || 'N/A'}</p>
                                <p class="ratings">⭐ ${movie.vote_average || 0}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    } else {
        body.innerHTML = `
            <div class="list-modal-content">
                <h2>${title}</h2>
                <p class="no-movies">${emptyMessage}</p>
            </div>
        `;
    }
}

// Close modals
function closeMovieModal() {
    movieModal.style.display = 'none';
}

function closeWatchlistModal() {
    watchlistModal.style.display = 'none';
}

function closeWatchedModal() {
    watchedModal.style.display = 'none';
}

// Close modal when clicking outside
window.onclick = e => {
    if (e.target == movieModal) closeMovieModal();
    if (e.target == watchlistModal) closeWatchlistModal();
    if (e.target == watchedModal) closeWatchedModal();
};

// Add to watchlist
function addToWatchlist(movieId) {
    fetch('/add_to_watchlist', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ movieId, username })
    })
    .then(res => res.json())
    .then(data => {
        showMessage(data.message);
        // Refresh page to update count
        setTimeout(() => location.reload(), 1500);
    })
    .catch(err => console.error(err));
}

// Add to watched
function addToWatched(movieId) {
    fetch('/add_to_watched', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ movieId, username })
    })
    .then(res => res.json())
    .then(data => {
        showMessage(data.message);
        // Refresh page to update count
        setTimeout(() => location.reload(), 1500);
    })
    .catch(err => console.error(err));
}

// Submit review
function submitReview(movieId) {
    const reviewText = document.getElementById('reviewText').value.trim();
    if(!reviewText) return alert('Write a review first!');

    const currentDate = new Date().toISOString().split('T')[0];

    fetch('/submit_reviews', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ reviewText, username, date: currentDate, movieId })
    })
    .then(res => res.json())
    .then(data => {
        showMessage(data.message);
        document.getElementById('reviewText').value = '';
        fetch(`/movie/${movieId}`).then(r => r.json()).then(displayMovieDetails);
    })
    .catch(err => console.error(err));
}

// Show temporary message
function showMessage(msg) {
    const msgDiv = document.getElementById('message');
    msgDiv.textContent = msg;
    msgDiv.style.display = 'block';
    setTimeout(() => msgDiv.style.display = 'none', 3000);
}
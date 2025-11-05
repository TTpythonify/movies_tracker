// Get modal elements
const modal = document.getElementById('movieModal');
const span = document.getElementsByClassName('close')[0];

// Function to open modal and load movie details
function openMovieModal(movieId) {
    modal.style.display = 'block';

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
                    <p>⭐ ${movie.vote_average || 0} / 10 (${movie.vote_count || 0} votes)</p>
                    <p><strong>Genres:</strong> ${movie.genres || 'N/A'}</p>
                    <p><strong>Overview:</strong><br>${movie.overview || 'No overview available.'}</p>

                    <div class="modal-actions">
                        <button onclick="addToWatchlist(${movie.id})">Add to Watch Later</button>
                        <button onclick="addToWatched(${movie.id})">Mark as Watched</button>
                    </div>
                </div>
            </div>

            <div class="reviews-section">
                <h3>User Reviews</h3>
                <div class="add-review-form">
                    <textarea id="reviewText" placeholder="Write your review..." rows="3"></textarea>
                    <button onclick="submitReview(${movie.id})">Submit Review</button>
                </div>
                <div id="reviewsList">
                    ${movie.reviews && movie.reviews.length > 0
                        ? movie.reviews.map(r => `<div class="review-item">
                            <strong>${r.username}</strong> <span>${r.date}</span>
                            <p>${r.reviewText}</p>
                        </div>`).join('')
                        : '<p>No reviews yet. Be the first!</p>'
                    }
                </div>
            </div>
        </div>
    `;
}

// Close modal
span.onclick = () => modal.style.display = 'none';
window.onclick = e => { if (e.target == modal) modal.style.display = 'none'; };

// Add to watchlist
function addToWatchlist(movieId) {
    fetch('/add_to_watchlist', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ movieId, username })
    })
    .then(res => res.json())
    .then(data => showMessage(data.message))
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
    .then(data => showMessage(data.message))
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

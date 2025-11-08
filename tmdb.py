import requests


BASE = "https://api.themoviedb.org/3"

def search_movie_by_api_key(query, api_key):
    if not api_key:
        return ("TMDB_API_KEY not provided")
    
    url = f"{BASE}/search/movie"
    res = requests.get(url, params={"api_key": api_key, "query": query})
    res.raise_for_status()
    
    return res.json().get("results", [])

def search_movie_by_bearer(query, access_token):
    if not access_token:
        raise ValueError("TMDB_ACCESS_TOKEN not provided")
    
    url = f"{BASE}/search/movie"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    res = requests.get(url, headers=headers, params={"query": query})
    res.raise_for_status()
    return res.json().get("results", [])

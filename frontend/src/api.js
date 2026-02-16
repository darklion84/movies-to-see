const API_BASE = '/api'

function getToken() {
  return localStorage.getItem('token')
}

function setToken(token) {
  localStorage.setItem('token', token)
}

function clearToken() {
  localStorage.removeItem('token')
}

function isAuthenticated() {
  return !!getToken()
}

async function request(url, options = {}) {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers
  })

  if (response.status === 401 || response.status === 403) {
    clearToken()
    throw new Error('Unauthorized')
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'Request failed')
  }

  return response.json()
}

async function login(password) {
  const data = await request('/login', {
    method: 'POST',
    body: JSON.stringify({ password })
  })
  setToken(data.token)
  return data
}

async function logout() {
  clearToken()
}

async function getMovies() {
  return request('/movies')
}

async function addMovie(tmdbId) {
  return request('/movies', {
    method: 'POST',
    body: JSON.stringify({ tmdb_id: tmdbId })
  })
}

async function deleteMovie(movieId) {
  return request(`/movies/${movieId}`, {
    method: 'DELETE'
  })
}

async function searchMovies(query) {
  return request(`/search?q=${encodeURIComponent(query)}`)
}

async function markAsWatched(movieId, impression = null) {
  return request(`/movies/${movieId}/watched`, {
    method: 'PATCH',
    body: JSON.stringify({ impression })
  })
}

async function markAsUnwatched(movieId) {
  return request(`/movies/${movieId}/unwatched`, {
    method: 'PATCH'
  })
}

export {
  login,
  logout,
  getMovies,
  addMovie,
  deleteMovie,
  searchMovies,
  markAsWatched,
  markAsUnwatched,
  isAuthenticated,
  clearToken
}

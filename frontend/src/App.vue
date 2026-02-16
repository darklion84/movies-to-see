<template>
  <div class="app">
    <LoginForm v-if="!authenticated" @login-success="onLoginSuccess" />
    <div v-else class="main">
      <div class="sticky-header">
        <header>
          <h1>Фильмы к просмотру</h1>
          <button @click="logout" class="logout-btn">Выйти</button>
        </header>
        <AddMovie @movie-added="onMovieAdded" />
        <div class="tabs">
          <button
            :class="['tab', { active: activeTab === 'toWatch' }]"
            @click="activeTab = 'toWatch'; watchedFilter = 'all'"
          >
            К просмотру ({{ toWatchMovies.length }})
          </button>
          <button
            :class="['tab', { active: activeTab === 'watched' }]"
            @click="activeTab = 'watched'"
          >
            Просмотрено ({{ watchedMovies.length }})
          </button>
        </div>
        <div v-if="activeTab === 'watched'" class="subtabs">
          <button
            :class="['subtab', { active: watchedFilter === 'all' }]"
            @click="watchedFilter = 'all'"
          >
            Все ({{ watchedMovies.length }})
          </button>
          <button
            :class="['subtab', { active: watchedFilter === 'liked' }]"
            @click="watchedFilter = 'liked'"
          >
            👍 Понравилось ({{ likedMovies.length }})
          </button>
          <button
            :class="['subtab', { active: watchedFilter === 'ok' }]"
            @click="watchedFilter = 'ok'"
          >
            👌 На разок ({{ okMovies.length }})
          </button>
          <button
            :class="['subtab', { active: watchedFilter === 'disliked' }]"
            @click="watchedFilter = 'disliked'"
          >
            👎 Фигня ({{ dislikedMovies.length }})
          </button>
        </div>
      </div>
      <div v-if="loading" class="loading">Загрузка...</div>
      <MovieList
        v-else
        :movies="displayedMovies"
        @watched="openRatingModal"
        @select="openModal"
      />
    </div>
    <MovieModal
      v-if="selectedMovie && !ratingMovie"
      :movie="selectedMovie"
      @close="closeModal"
      @watched="openRatingModal"
      @unwatched="handleMarkUnwatched"
      @delete="handleDeleteFromModal"
    />
    <RatingModal
      v-if="ratingMovie"
      :movie="ratingMovie"
      @close="closeRatingModal"
      @select="handleRatingSelect"
    />
  </div>
</template>

<script>
import LoginForm from './components/LoginForm.vue'
import AddMovie from './components/AddMovie.vue'
import MovieList from './components/MovieList.vue'
import MovieModal from './components/MovieModal.vue'
import RatingModal from './components/RatingModal.vue'
import { getMovies, deleteMovie, markAsWatched, markAsUnwatched, isAuthenticated, clearToken } from './api.js'

export default {
  name: 'App',
  components: {
    LoginForm,
    AddMovie,
    MovieList,
    MovieModal,
    RatingModal
  },
  data() {
    return {
      authenticated: false,
      movies: [],
      loading: false,
      selectedMovie: null,
      ratingMovie: null,
      activeTab: 'toWatch',
      watchedFilter: 'all'
    }
  },
  computed: {
    toWatchMovies() {
      return this.movies.filter(m => !m.watched)
    },
    watchedMovies() {
      return this.movies.filter(m => m.watched)
    },
    likedMovies() {
      return this.movies.filter(m => m.watched && m.impression === 'liked')
    },
    okMovies() {
      return this.movies.filter(m => m.watched && m.impression === 'ok')
    },
    dislikedMovies() {
      return this.movies.filter(m => m.watched && m.impression === 'disliked')
    },
    displayedMovies() {
      if (this.activeTab === 'toWatch') {
        return this.toWatchMovies
      }
      if (this.watchedFilter === 'all') {
        return this.watchedMovies
      }
      return this.movies.filter(m => m.watched && m.impression === this.watchedFilter)
    }
  },
  mounted() {
    this.authenticated = isAuthenticated()
    if (this.authenticated) {
      this.loadMovies()
    }
  },
  methods: {
    onLoginSuccess() {
      this.authenticated = true
      this.loadMovies()
    },
    async onMovieAdded(movie) {
      await this.loadMovies()
      this.openModal(movie)
    },
    async loadMovies() {
      this.loading = true
      try {
        this.movies = await getMovies()
      } catch (e) {
        if (e.message === 'Unauthorized') {
          this.authenticated = false
        }
      } finally {
        this.loading = false
      }
    },
    async handleDelete(movieId) {
      try {
        await deleteMovie(movieId)
        this.movies = this.movies.filter(m => m.id !== movieId)
      } catch (e) {
        console.error('Failed to delete movie', e)
      }
    },
    async handleDeleteFromModal(movieId) {
      await this.handleDelete(movieId)
      this.closeModal()
    },
    openRatingModal(movieId) {
      const movie = this.movies.find(m => m.id === movieId)
      if (movie) {
        this.ratingMovie = movie
      }
    },
    closeRatingModal() {
      this.ratingMovie = null
    },
    async handleRatingSelect(impression) {
      if (!this.ratingMovie) return
      try {
        const updated = await markAsWatched(this.ratingMovie.id, impression)
        const index = this.movies.findIndex(m => m.id === this.ratingMovie.id)
        if (index !== -1) {
          this.movies[index] = updated
        }
        this.closeRatingModal()
        this.closeModal()
      } catch (e) {
        console.error('Failed to mark as watched', e)
      }
    },
    async handleMarkUnwatched(movieId) {
      try {
        const updated = await markAsUnwatched(movieId)
        const index = this.movies.findIndex(m => m.id === movieId)
        if (index !== -1) {
          this.movies[index] = updated
        }
        this.closeModal()
      } catch (e) {
        console.error('Failed to mark as unwatched', e)
      }
    },
    openModal(movie) {
      this.selectedMovie = movie
    },
    closeModal() {
      this.selectedMovie = null
    },
    logout() {
      clearToken()
      this.authenticated = false
      this.movies = []
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  background: #0f0f23;
  color: #fff;
  min-height: 100vh;
}

.app {
  min-height: 100vh;
}

.main {
  max-width: 1200px;
  margin: 0 auto;
}

.sticky-header {
  position: sticky;
  top: 0;
  background: #0f0f23;
  z-index: 100;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #333;
}

header h1 {
  color: #e94560;
  font-size: 1.25rem;
}

.logout-btn {
  padding: 8px 16px;
  border: 1px solid #333;
  border-radius: 6px;
  background: transparent;
  color: #888;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.logout-btn:hover {
  border-color: #e94560;
  color: #e94560;
}

.tabs {
  display: flex;
  padding: 0 1rem;
  border-bottom: 1px solid #333;
}

.tab {
  padding: 12px 20px;
  border: none;
  background: transparent;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab:hover {
  color: #fff;
}

.tab.active {
  color: #e94560;
  border-bottom-color: #e94560;
}

.subtabs {
  display: flex;
  padding: 0 1rem;
  border-bottom: 1px solid #333;
  background: #0a0a18;
  overflow-x: auto;
}

.subtab {
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  white-space: nowrap;
}

.subtab:hover {
  color: #aaa;
}

.subtab.active {
  color: #fff;
  border-bottom-color: #fff;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #888;
}
</style>

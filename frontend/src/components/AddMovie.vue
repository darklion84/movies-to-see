<template>
  <div class="add-movie">
    <div class="search-container">
      <input
        v-model="query"
        type="text"
        placeholder="Поиск фильма или сериала..."
        @input="debouncedSearch"
        :disabled="adding"
      />
      <button v-if="query" @click="clearSearch" class="clear-btn">
        &times;
      </button>
    </div>

    <div v-if="searching" class="loading">Поиск...</div>

    <div v-if="results.length > 0" class="results">
      <div
        v-for="movie in results"
        :key="movie.tmdb_id"
        class="result-item"
        @click="selectMovie(movie)"
      >
        <img
          v-if="movie.poster_url"
          :src="movie.poster_url"
          :alt="movie.title"
          class="result-poster"
        />
        <div v-else class="result-no-poster">?</div>
        <div class="result-info">
          <div class="result-title">{{ movie.title }}</div>
          <div class="result-meta">
            <span v-if="movie.media_type === 'tv'" class="result-type">сериал</span>
            <span class="result-rating">{{ movie.rating.toFixed(1) }}</span>
            <span v-if="movie.release_date" class="result-year">
              {{ movie.release_date.substring(0, 4) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="adding" class="loading">Добавление...</div>
  </div>
</template>

<script>
import { searchMovies, addMovie } from '../api.js'

export default {
  name: 'AddMovie',
  emits: ['movie-added'],
  data() {
    return {
      query: '',
      results: [],
      searching: false,
      adding: false,
      error: '',
      searchTimeout: null
    }
  },
  methods: {
    debouncedSearch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.search()
      }, 300)
    },
    async search() {
      if (this.query.length < 2) {
        this.results = []
        return
      }

      this.searching = true
      this.error = ''

      try {
        this.results = await searchMovies(this.query)
      } catch (e) {
        this.error = 'Ошибка поиска'
      } finally {
        this.searching = false
      }
    },
    async selectMovie(movie) {
      this.adding = true
      this.error = ''

      try {
        const addedMovie = await addMovie(movie.tmdb_id, movie.media_type || 'movie')
        this.clearSearch()
        this.$emit('movie-added', addedMovie)
      } catch (e) {
        this.error = 'Ошибка добавления'
      } finally {
        this.adding = false
      }
    },
    clearSearch() {
      this.query = ''
      this.results = []
      this.error = ''
    }
  }
}
</script>

<style scoped>
.add-movie {
  padding: 1rem;
  border-bottom: 1px solid #333;
}

.search-container {
  position: relative;
}

input {
  width: 100%;
  padding: 12px;
  padding-right: 40px;
  border: 1px solid #333;
  border-radius: 8px;
  background: #1a1a2e;
  color: #fff;
  font-size: 16px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #e94560;
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #666;
  font-size: 24px;
  cursor: pointer;
  padding: 4px 8px;
}

.clear-btn:hover {
  color: #fff;
}

.results {
  margin-top: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.result-item:hover {
  background: #1a1a2e;
}

.result-poster {
  width: 40px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.result-no-poster {
  width: 40px;
  height: 60px;
  background: #333;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.result-info {
  margin-left: 12px;
  flex: 1;
}

.result-title {
  color: #fff;
  font-size: 14px;
  line-height: 1.3;
}

.result-meta {
  margin-top: 4px;
  font-size: 12px;
  color: #888;
}

.result-type {
  background: #4a4a6a;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  text-transform: uppercase;
  margin-right: 6px;
}

.result-rating {
  color: #e94560;
  font-weight: bold;
}

.result-year {
  margin-left: 8px;
}

.loading {
  text-align: center;
  padding: 1rem;
  color: #888;
}

.error {
  text-align: center;
  padding: 1rem;
  color: #ff6b6b;
}
</style>

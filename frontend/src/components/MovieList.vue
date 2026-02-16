<template>
  <div class="movie-list">
    <div v-if="movies.length === 0" class="empty-state">
      <p>Список пуст</p>
      <p class="hint">Добавьте фильмы через поиск</p>
    </div>
    <div v-else class="grid">
      <MovieCard
        v-for="movie in movies"
        :key="movie.id"
        :movie="movie"
        @watched="$emit('watched', $event)"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script>
import MovieCard from './MovieCard.vue'

export default {
  name: 'MovieList',
  components: { MovieCard },
  props: {
    movies: {
      type: Array,
      required: true
    }
  },
  emits: ['watched', 'select']
}
</script>

<style scoped>
.movie-list {
  padding: 1rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #666;
}

.empty-state p {
  margin: 0;
  font-size: 18px;
}

.hint {
  margin-top: 8px !important;
  font-size: 14px !important;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}

@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}
</style>

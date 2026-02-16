<template>
  <div class="movie-card">
    <div class="poster-container" @click="$emit('select', movie)">
      <img
        v-if="movie.poster_url"
        :src="movie.poster_url"
        :alt="movie.title"
        class="poster"
      />
      <div v-else class="no-poster">
        <span>Нет постера</span>
      </div>
      <div class="rating">{{ movie.rating.toFixed(1) }}</div>
    </div>
    <div class="info">
      <h3 class="title" @click="$emit('select', movie)">{{ movie.title }}</h3>
      <div v-if="movie.watched" class="watched-info">
        <span class="impression-icon">{{ impressionIcon }}</span>
        <span class="watched-date">{{ formattedWatchedDate }}</span>
      </div>
      <button v-else @click="$emit('watched', movie.id)" class="watched-btn">
        Посмотрел ✓
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MovieCard',
  props: {
    movie: {
      type: Object,
      required: true
    }
  },
  emits: ['watched', 'select'],
  computed: {
    impressionIcon() {
      const icons = {
        liked: '👍',
        ok: '👌',
        disliked: '👎'
      }
      return icons[this.movie.impression] || ''
    },
    formattedWatchedDate() {
      if (!this.movie.watched_at) return ''
      const date = new Date(this.movie.watched_at)
      const months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
      return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`
    }
  }
}
</script>

<style scoped>
.movie-card {
  background: #1a1a2e;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.movie-card:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
  z-index: 10;
}

.poster-container {
  position: relative;
  aspect-ratio: 2/3;
  cursor: pointer;
}

.poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-poster {
  width: 100%;
  height: 100%;
  background: #0f0f23;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.rating {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(233, 69, 96, 0.9);
  color: #fff;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: bold;
  font-size: 14px;
}

.info {
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.title {
  color: #fff;
  font-size: 14px;
  margin: 0 0 12px 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  cursor: pointer;
}

.title:hover {
  color: #e94560;
}

.watched-btn {
  width: 100%;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: #1e8449;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: auto;
}

.watched-btn:hover {
  background: #2ecc71;
}

.watched-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px;
  background: #16213e;
  border-radius: 6px;
  margin-top: auto;
}

.impression-icon {
  font-size: 14px;
}

.watched-date {
  color: #888;
  font-size: 12px;
}
</style>

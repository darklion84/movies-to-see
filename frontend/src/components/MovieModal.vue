<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button class="close-btn" @click="$emit('close')">&times;</button>
      <div class="modal-body">
        <div class="poster-side">
          <img
            v-if="movie.poster_url"
            :src="movie.poster_url"
            :alt="movie.title"
            class="modal-poster"
          />
          <div v-else class="no-poster-large">Нет постера</div>
        </div>
        <div class="info-side">
          <h2 class="modal-title">{{ movie.title }}</h2>
          <div class="meta-row">
            <span v-if="movie.release_year" class="year">{{ movie.release_year }}</span>
            <span class="rating-badge">{{ movie.rating.toFixed(1) }}</span>
            <span v-if="movie.watched" class="watched-badge">Просмотрено</span>
          </div>
          <div v-if="movie.actors" class="actors">
            <span class="label">Актёры:</span> {{ movie.actors }}
          </div>
          <div v-if="movie.description" class="description">
            {{ movie.description }}
          </div>
          <div class="actions">
            <button
              @click="searchOnline"
              class="action-btn search"
            >
              Искать онлайн
            </button>
            <button
              v-if="!movie.watched"
              @click="$emit('watched', movie.id)"
              class="action-btn primary"
            >
              Просмотрено
            </button>
            <button
              v-else
              @click="$emit('unwatched', movie.id)"
              class="action-btn secondary"
            >
              Вернуть в список
            </button>
            <button
              @click="$emit('delete', movie.id)"
              class="action-btn danger"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MovieModal',
  props: {
    movie: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'delete', 'watched', 'unwatched'],
  mounted() {
    document.addEventListener('keydown', this.handleKeydown)
    document.body.style.overflow = 'hidden'
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
    document.body.style.overflow = ''
  },
  methods: {
    handleKeydown(e) {
      if (e.key === 'Escape') {
        this.$emit('close')
      }
    },
    searchOnline() {
      const query = encodeURIComponent(`${this.movie.title} смотреть онлайн`)
      window.open(`https://duckduckgo.com/?q=${query}`, '_blank')
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: #1a1a2e;
  border-radius: 12px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  background: none;
  border: none;
  color: #888;
  font-size: 28px;
  cursor: pointer;
  z-index: 10;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
}

.poster-side {
  flex-shrink: 0;
  width: 200px;
}

.modal-poster {
  width: 100%;
  border-radius: 8px;
}

.no-poster-large {
  width: 100%;
  aspect-ratio: 2/3;
  background: #0f0f23;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.info-side {
  flex: 1;
  min-width: 0;
}

.modal-title {
  color: #fff;
  font-size: 1.5rem;
  margin: 0 0 0.75rem 0;
  padding-right: 2rem;
}

.meta-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.year {
  color: #888;
  font-size: 1rem;
}

.rating-badge {
  background: #e94560;
  color: #fff;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: bold;
  font-size: 0.9rem;
}

.watched-badge {
  background: #2ecc71;
  color: #fff;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.8rem;
}

.actors {
  color: #ccc;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.actors .label {
  color: #888;
}

.description {
  color: #aaa;
  font-size: 0.9rem;
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
  text-align: center;
  white-space: nowrap;
}

.action-btn.primary {
  background: #666;
  color: #fff;
}

.action-btn.primary:hover {
  background: #888;
}

.action-btn.secondary {
  background: #3498db;
  color: #fff;
}

.action-btn.secondary:hover {
  background: #5dade2;
}

.action-btn.search {
  background: #27ae60;
  color: #fff;
}

.action-btn.search:hover {
  background: #2ecc71;
}

.action-btn.danger {
  background: #c0392b;
  color: #fff;
}

.action-btn.danger:hover {
  background: #e74c3c;
}

@media (max-width: 600px) {
  .modal-body {
    flex-direction: column;
  }

  .poster-side {
    width: 100%;
    max-width: 200px;
    margin: 0 auto;
  }

  .modal-title {
    font-size: 1.25rem;
  }

  .actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}
</style>

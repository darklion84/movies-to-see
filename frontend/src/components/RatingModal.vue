<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h2>Впечатление?</h2>
      <p class="movie-title">{{ movie.title }}</p>
      <div class="options">
        <button @click="$emit('select', 'liked')" class="option liked">
          <span class="emoji">👍</span>
          <span>Понравилось</span>
        </button>
        <button @click="$emit('select', 'ok')" class="option ok">
          <span class="emoji">👌</span>
          <span>На разок</span>
        </button>
        <button @click="$emit('select', 'disliked')" class="option disliked">
          <span class="emoji">👎</span>
          <span>Фигня</span>
        </button>
      </div>
      <button @click="$emit('close')" class="cancel-btn">Отмена</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RatingModal',
  props: {
    movie: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'select'],
  mounted() {
    document.addEventListener('keydown', this.handleKeydown)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
  },
  methods: {
    handleKeydown(e) {
      if (e.key === 'Escape') {
        this.$emit('close')
      }
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
  z-index: 1001;
  padding: 1rem;
}

.modal-content {
  background: #1a1a2e;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  max-width: 400px;
  width: 100%;
}

h2 {
  color: #fff;
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.movie-title {
  color: #888;
  margin: 0 0 1.5rem 0;
  font-size: 0.9rem;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 1.5rem;
}

.option {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #fff;
}

.option .emoji {
  font-size: 1.3rem;
}

.option.liked {
  background: #27ae60;
}

.option.liked:hover {
  background: #2ecc71;
}

.option.ok {
  background: #f39c12;
}

.option.ok:hover {
  background: #f1c40f;
}

.option.disliked {
  background: #c0392b;
}

.option.disliked:hover {
  background: #e74c3c;
}

.cancel-btn {
  background: transparent;
  border: 1px solid #444;
  color: #888;
  padding: 10px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.cancel-btn:hover {
  border-color: #666;
  color: #fff;
}
</style>

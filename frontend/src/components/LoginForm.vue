<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Фильмы к просмотру</h1>
      <form @submit.prevent="handleLogin">
        <input
          v-model="password"
          type="password"
          placeholder="Введите пароль"
          :disabled="loading"
          autofocus
        />
        <button type="submit" :disabled="loading || !password">
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import { login } from '../api.js'

export default {
  name: 'LoginForm',
  emits: ['login-success'],
  data() {
    return {
      password: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      try {
        await login(this.password)
        this.$emit('login-success')
      } catch (e) {
        this.error = 'Неверный пароль'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.login-box {
  background: #0f0f23;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  text-align: center;
  width: 90%;
  max-width: 320px;
}

h1 {
  color: #e94560;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

input {
  width: 100%;
  padding: 12px;
  border: 1px solid #333;
  border-radius: 8px;
  background: #1a1a2e;
  color: #fff;
  font-size: 16px;
  margin-bottom: 1rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #e94560;
}

button {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: #e94560;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover:not(:disabled) {
  background: #ff6b6b;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  color: #ff6b6b;
  margin-top: 1rem;
  font-size: 14px;
}
</style>

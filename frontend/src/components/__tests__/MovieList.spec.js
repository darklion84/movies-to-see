import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MovieList from '../MovieList.vue'
import MovieCard from '../MovieCard.vue'

describe('MovieList', () => {
  it('renders empty state when no movies', () => {
    const wrapper = mount(MovieList, {
      props: { movies: [] }
    })
    expect(wrapper.text()).toContain('Список пуст')
  })

  it('renders movie cards for each movie', () => {
    const movies = [
      { id: 1, tmdb_id: 100, title: 'Movie 1', poster_url: null, rating: 7.5 },
      { id: 2, tmdb_id: 101, title: 'Movie 2', poster_url: null, rating: 8.0 }
    ]
    const wrapper = mount(MovieList, {
      props: { movies },
      global: {
        components: { MovieCard }
      }
    })
    const cards = wrapper.findAllComponents(MovieCard)
    expect(cards.length).toBe(2)
  })

  it('emits delete event when movie card emits delete', async () => {
    const movies = [
      { id: 1, tmdb_id: 100, title: 'Movie 1', poster_url: null, rating: 7.5 }
    ]
    const wrapper = mount(MovieList, {
      props: { movies },
      global: {
        components: { MovieCard }
      }
    })
    const card = wrapper.findComponent(MovieCard)
    await card.vm.$emit('delete', 1)
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')[0]).toEqual([1])
  })
})

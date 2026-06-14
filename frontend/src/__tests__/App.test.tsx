import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import App from '../App'
import * as api from '../api'

// Mock the API calls
vi.mock('../api', () => ({
  getProjectState: vi.fn().mockResolvedValue({
    project_name: 'Test Project',
    tasks: []
  }),
  initializeProject: vi.fn(),
  generatePlan: vi.fn(),
  executeTasks: vi.fn()
}))

describe('App', () => {
  it('renders correctly', async () => {
    render(<App />)
    expect(await screen.findByText('ProjectWriter-V2')).toBeInTheDocument()
    expect(await screen.findByText(/Status: Idle/i)).toBeInTheDocument()
  })
})

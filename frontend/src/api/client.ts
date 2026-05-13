import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

export const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

export async function fetcher<T>(url: string): Promise<T> {
  const resp = await api.get<T>(url)
  return resp.data
}

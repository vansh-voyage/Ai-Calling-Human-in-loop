import useSWR from 'swr'
import { fetcher } from '../api/client'
import type { HelpRequestListResponse, HelpRequestStats, RequestStatus } from '../types'

export function useHelpRequests(status?: RequestStatus, limit = 50) {
  const key = `/help-requests?status=${status ?? ''}&limit=${limit}`
  const { data, error, mutate } = useSWR<HelpRequestListResponse>(key, fetcher, {
    refreshInterval: 30_000,
  })
  return {
    requests: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading: !data && !error,
    error,
    mutate,
  }
}

export function useStats() {
  const { data, error, mutate } = useSWR<HelpRequestStats>(
    '/help-requests/stats',
    fetcher,
    { refreshInterval: 30_000 }
  )
  return { stats: data, isLoading: !data && !error, error, mutate }
}

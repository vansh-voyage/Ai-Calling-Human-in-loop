import useSWR from 'swr'
import { fetcher } from '../api/client'
import type { KnowledgeEntryListResponse } from '../types'

export function useKnowledge(limit = 100) {
  const { data, error, mutate } = useSWR<KnowledgeEntryListResponse>(
    `/knowledge?limit=${limit}`,
    fetcher,
    { refreshInterval: 60_000 }
  )
  return {
    entries: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading: !data && !error,
    error,
    mutate,
  }
}

export type RequestStatus = 'pending' | 'resolved' | 'unresolved'

export interface HelpRequest {
  id: number
  caller_id: string
  caller_name: string | null
  question: string
  question_normalized: string
  status: RequestStatus
  answer: string | null
  answered_by: string | null
  sms_sent: boolean
  created_at: string
  resolved_at: string | null
  timeout_at: string
}

export interface HelpRequestListResponse {
  items: HelpRequest[]
  total: number
  limit: number
  offset: number
}

export interface HelpRequestStats {
  pending: number
  resolved: number
  unresolved: number
  total: number
}

export interface KnowledgeEntry {
  id: number
  question_normalized: string
  question_display: string
  answer: string
  source: string
  help_request_id: number | null
  created_at: string
  updated_at: string
  lookup_count: number
}

export interface KnowledgeEntryListResponse {
  items: KnowledgeEntry[]
  total: number
  limit: number
  offset: number
}

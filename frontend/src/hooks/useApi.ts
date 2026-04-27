import { useState, useCallback, useRef, useEffect } from 'react'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}

export function useApi<T = unknown>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const isMountedRef = useRef(true)

  useEffect(() => {
    return () => {
      isMountedRef.current = false
    }
  }, [])

  const request = useCallback(
    async (apiCall: () => Promise<ApiResponse<T>>): Promise<T | null> => {
      if (!isMountedRef.current) return null

      setState({ data: null, loading: true, error: null })
      try {
        const result = await apiCall()
        if (!isMountedRef.current) return null

        if (result.success && result.data) {
          setState({ data: result.data, loading: false, error: null })
          return result.data
        } else {
          setState({ data: null, loading: false, error: result.error || 'Unknown error' })
          return null
        }
      } catch (err) {
        if (!isMountedRef.current) return null

        const errorMsg = err instanceof Error ? err.message : 'An error occurred'
        setState({ data: null, loading: false, error: errorMsg })
        return null
      }
    },
    []
  )

  return { ...state, request }
}

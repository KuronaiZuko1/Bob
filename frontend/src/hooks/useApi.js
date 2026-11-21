import { useState, useEffect, useCallback } from 'react'
import client from '../api/client'

/**
 * Generic data-fetching hook.
 * Returns { data, loading, error, refetch }
 */
function useFetch(url, params = {}) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await client.get(url, { params })
      setData(res.data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, JSON.stringify(params)])

  useEffect(() => { fetch() }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useHealth()       { return useFetch('/api/health') }
export function useStats()        { return useFetch('/api/stats') }
export function useActivity()     { return useFetch('/api/stats/activity') }
export function useProfile()      { return useFetch('/api/profile') }
export function useVacancies(p)   { return useFetch('/api/vacancies', p) }
export function useApplications(p){ return useFetch('/api/applications', p) }
export function useDocuments()    { return useFetch('/api/documents') }
export function useSettings()     { return useFetch('/api/settings') }

export default useFetch

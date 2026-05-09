const API_URL = 'http://127.0.0.1:8000'

const api = {
  get: async (url: string, options: any = {}) => {
    const params = options.params
      ? '?' + new URLSearchParams(options.params).toString()
      : ''

    const res = await fetch(API_URL + url + params)

    if (!res.ok) {
      throw new Error(`GET ${url} → ${res.status}`)
    }

    return { data: await res.json() }
  },

  post: async (url: string, body: any) => {
  console.log("POST →", API_URL + url, body)

  const res = await fetch(API_URL + url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    throw new Error(`POST ${url} → ${res.status}`)
  }

  return await res.json()
},

  patch: async (url: string, body: any) => {
    const res = await fetch(API_URL + url, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })

    if (!res.ok) {
      throw new Error(`PATCH ${url} → ${res.status}`)
    }

    return { data: await res.json() }
  },

  delete: async (url: string) => {
  const res = await fetch(API_URL + url, {
    method: 'DELETE',
  })

  if (!res.ok) {
    throw new Error(`DELETE ${url} → ${res.status}`)
  }

  return null
},
}

export default api
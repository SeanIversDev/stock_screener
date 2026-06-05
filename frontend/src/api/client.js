import axios from 'axios'

const client = axios.create({
    baseURL: 'http://localhost:8000'
})

export const fetchScreenerResults = async (filters = {}) => {
    const params = Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
    )
    const { data } = await client.get('/api/screen', { params })
    return data
}

export const fetchStockDetail = async (ticker) => {
    const { data } = await client.get(`/api/stocks/${ticker}`)
    return data
}

export const fetchStockBars = async (ticker, period = '6m') => {
    const { data } = await client.get(`/api/stocks/${ticker}/bars`, { params: { period } })
    return data
}
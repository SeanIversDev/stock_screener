import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchScreenerResults } from './api/client'
import ScreenerTable from './components/ScreenerTable'
import FilterPanel from './components/FilterPanel'
import StockDetail from './pages/StockDetail'

const DEFAULT_FILTERS = {}

function ScreenerPage() {
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [appliedFilters, setAppliedFilters] = useState(DEFAULT_FILTERS)

  const { data, isLoading, error } = useQuery({
    queryKey: ['screen', appliedFilters],
    queryFn: () => fetchScreenerResults(appliedFilters),
  })

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8">
      <h1 className="text-3xl font-bold text-white mb-8">Stock Screener</h1>
      <div className="flex gap-6">
        <div className="w-72 shrink-0">
          <FilterPanel
            filters={filters}
            onChange={setFilters}
            onApply={() => setAppliedFilters(filters)}
            onReset={() => { setFilters(DEFAULT_FILTERS); setAppliedFilters(DEFAULT_FILTERS) }}
          />
        </div>
        <div className="flex-1">
          <p className="text-gray-400 text-sm mb-4">
            {data ? `${data.length} stocks found` : ''}
          </p>
          <ScreenerTable data={data} isLoading={isLoading} error={error} />
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ScreenerPage />} />
      <Route path="/stocks/:ticker" element={<StockDetail />} />
    </Routes>
  )
}
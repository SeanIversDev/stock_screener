import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchStockDetail, fetchStockBars } from '../api/client'
import PriceChart from '../components/PriceChart'

const fmt = (val, type) => {
    if (val === null || val === undefined) return '-'
    switch (type) {
        case 'currency': return `$${(val / 1e9).toFixed(1)}B`
        case 'percent': return `${(val * 100).toFixed(2)}%`
        case 'dividend': return `${val.toFixed(2)}%`
        case 'number': return val.toFixed(2)
        case 'integer': return val.toLocaleString()
        default: return val
    }
}

const StatCard = ({ label, value }) => (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        <p className="text-gray-400 text-xs mb-1">{label}</p>
        <p className="text-white font-semibold text-lg">{value}</p>
    </div>
)

const PERIODS = ['1m', '3m', '6m', '1y', '2y']

export default function StockDetail() {
    const { ticker } = useParams()
    const navigate = useNavigate()
    const [period, setPeriod] = useState('6m')

    const { data: detail, isLoading: detailLoading, error: detailError } = useQuery({
        queryKey: ['detail', ticker],
        queryFn: () => fetchStockDetail(ticker),
    })

    const { data: bars, isLoading: barsLoading } = useQuery({
        queryKey: ['bars', ticker, period],
        queryFn: () => fetchStockBars(ticker, period),
    })

    if (detailLoading) return (
        <div className="min-h-screen bg-gray-950 text-white p-8">
            <div className="space-y-4">
                {[...Array(6)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-800 rounded animate-pulse" />
                ))}
            </div>
        </div>
    )

    if (detailError) return (
        <div className="min-h-screen bg-gray-950 text-white p-8">
            <div className="text-red-400 p-4 bg-red-950 rounded-lg">
                Failed to load stock data.
            </div>
        </div>
    )

    return (
        <div className="min-h-screen bg-gray-950 text-white p-8 max-w-6xl mx-auto">

            {/* Header */}
            <button
                onClick={() => navigate(-1)}
                className="text-gray-400 hover:text-white text-sm mb-6 flex items-center gap-1 transition-colors"
            >
                ← Back to Screener
            </button>

            <div className="flex items-start justify-between mb-8">
                <div>
                    <h1 className="text-4xl font-bold text-white">{ticker}</h1>
                    <p className="text-gray-400 mt-1">{detail?.name}</p>
                    <div className="flex gap-2 mt-2">
                        {detail?.sector && (
                            <span className="text-xs bg-blue-900 text-blue-300 px-2 py-1 rounded">
                                {detail.sector}
                            </span>
                        )}
                        {detail?.industry && (
                            <span className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded">
                                {detail.industry}
                            </span>
                        )}
                    </div>
                </div>
                {detail?.website && (
                    <a
                        href={detail.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
                    >
                        {detail.website.replace('https://', '')} ↗
                    </a>
                )}
            </div>

            {/* Key stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <StatCard label="Market Cap"
                    value={fmt(detail?.market_cap, 'currency')} />
                <StatCard label="P/E Ratio"
                    value={fmt(detail?.pe_ratio, 'number')} />
                <StatCard label="P/B Ratio"
                    value={fmt(detail?.pb_ratio, 'number')} />
                <StatCard label="ROE"
                    value={fmt(detail?.roe, 'percent')} />
                <StatCard label="Debt / Equity"
                    value={fmt(detail?.debt_equity, 'number')} />
                <StatCard label="EV / EBITDA"
                    value={fmt(detail?.ev_ebitda, 'number')} />
                <StatCard label="Dividend Yield"
                    value={fmt(detail?.dividend_yield, 'dividend')} />
                <StatCard label="Beta"
                    value={fmt(detail?.beta, 'number')} />
            </div>

            {/* 52-week range */}
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 mb-8">
                <p className="text-gray-400 text-xs mb-3">52-Week Range</p>
                <div className="flex items-center gap-4">
                    <span className="text-red-400 font-semibold">${detail?.week52_low?.toFixed(2)}</span>
                    <div className="flex-1 h-2 bg-gray-700 rounded-full" />
                    <span className="text-green-400 font-semibold">${detail?.week52_high?.toFixed(2)}</span>
                </div>
            </div>

            {/* Price chart */}
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-8">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold">Price History</h2>
                    <div className="flex gap-1">
                        {PERIODS.map(p => (
                            <button
                                key={p}
                                onClick={() => setPeriod(p)}
                                className={`px-3 py-1 text-xs rounded transition-colors ${period === p
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-800 text-gray-400 hover:text-white'
                                    }`}
                            >
                                {p.toUpperCase()}
                            </button>
                        ))}
                    </div>
                </div>
                {barsLoading
                    ? <div className="h-64 bg-gray-800 rounded animate-pulse" />
                    : <PriceChart bars={bars} />
                }
            </div>

            {/* Company description */}
            {detail?.description && (
                <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-8">
                    <h2 className="text-lg font-semibold mb-3">About</h2>
                    <p className="text-gray-400 text-sm leading-relaxed">{detail.description}</p>
                </div>
            )}

            {/* Footer stats */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <StatCard label="Employees" value={fmt(detail?.employees, 'integer')} />
                <StatCard label="Avg Volume" value={fmt(detail?.avg_volume, 'integer')} />
                <StatCard label="Free Cash Flow" value={fmt(detail?.free_cashflow, 'currency')} />
            </div>

        </div>
    )
}
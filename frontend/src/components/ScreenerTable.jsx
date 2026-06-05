import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const COLUMNS = [
    { key: 'ticker', label: 'Ticker' },
    { key: 'name', label: 'Name' },
    { key: 'sector', label: 'Sector' },
    { key: 'market_cap', label: 'Market Cap' },
    { key: 'pe_ratio', label: 'P/E' },
    { key: 'pb_ratio', label: 'P/B' },
    { key: 'roe', label: 'ROE' },
    { key: 'debt_equity', label: 'D/E' },
    { key: 'dividend_yield', label: 'Div Yield' },
    { key: 'beta', label: 'Beta' },
]

const formatValue = (key, value) => {
    if (value === null || value === undefined) return '-'
    switch (key) {
        case 'market_cap': return `$${(value / 1e9).toFixed(1)}B`
        case 'roe': return `${(value * 100).toFixed(1)}%`
        case 'dividend_yield': return `${value.toFixed(2)}%`
        default: return typeof value === 'number' ? value.toFixed(2) : value
    }
}

const sortData = (data, key, ascending) => {
    return [...data].sort((a, b) => {
        const aVal = a[key]
        const bVal = b[key]
        if (aVal === null || aVal === undefined) return 1
        if (bVal === null || bVal === undefined) return -1
        if (typeof aVal === 'string') return ascending
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal)
        return ascending ? aVal - bVal : bVal - aVal
    })
}

const SortIcon = ({ column, sortKey, ascending }) => {
    if (sortKey !== column) return <span className="ml-1 text-gray-600">↕</span>
    return <span className="ml-1 text-blue-400">{ascending ? '▲' : '▼'}</span>
}

export default function ScreenerTable({ data, isLoading, error }) {
    const [sortKey, setSortKey] = useState('market_cap')
    const [ascending, setAscending] = useState(false)
    const navigate = useNavigate()

    const handleSort = (key) => {
        if (sortKey === key) {
            setAscending(!ascending)
        } else {
            setSortKey(key)
            setAscending(false)
        }
    }

    if (isLoading) return (
        <div className="space-y-2">
            {[...Array(10)].map((_, i) => (
                <div key={i} className="h-12 bg-gray-800 rounded animate-pulse" />
            ))}
        </div>
    )

    if (error) return (
        <div className="text-red-400 p-4 bg-red-950 rounded-lg">
            Failed to load data. Is the backend running?
        </div>
    )

    if (!data?.length) return (
        <div className="text-gray-400 p-4">No stocks match your filters.</div>
    )

    const sorted = sortData(data, sortKey, ascending)

    return (
        <div className="overflow-x-auto rounded-lg border border-gray-800">
            <table className="w-full text-sm">
                <thead>
                    <tr className="bg-gray-900 text-gray-400 text-left">
                        {COLUMNS.map(col => (
                            <th
                                key={col.key}
                                onClick={() => handleSort(col.key)}
                                className="px-4 py-3 font-medium cursor-pointer hover:text-white select-none transition-colors"
                            >
                                {col.label}
                                <SortIcon column={col.key} sortKey={sortKey} ascending={ascending} />
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {sorted.map((stock, i) => (
                        <tr
                            key={stock.ticker}
                            onClick={() => navigate(`/stocks/${stock.ticker}`)}
                            className={`border-t border-gray-800 hover:bg-gray-800 transition-colors cursor-pointer
                                ${i % 2 === 0 ? 'bg-gray-950' : 'bg-gray-900'}`}
                        >
                            {COLUMNS.map(col => (
                                <td key={col.key} className="px-4 py-3">
                                    {col.key === 'ticker'
                                        ? <span className="font-bold text-blue-400">{stock.ticker}</span>
                                        : formatValue(col.key, stock[col.key])
                                    }
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
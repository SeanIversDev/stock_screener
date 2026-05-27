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
        case 'dividend_yield': return `${(value * 100).toFixed(2)}%`
        default: return typeof value === 'number' ? value.toFixed(2) : value
    }
}

export default function ScreenerTable({ data, isLoading, error }) {
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

    return (
        <div className="overflow-x-auto rounded-lg border border-gray-800">
            <table className="w-full text-sm">
                <thead>
                    <tr className="bg-gray-900 text-gray-400 text-left">
                        {COLUMNS.map(col => (
                            <th key={col.key} className="px-4 py-3 font-medium">{col.label}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((stock, i) => (
                        <tr
                            key={stock.ticker}
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
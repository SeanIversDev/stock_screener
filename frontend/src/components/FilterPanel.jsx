const SECTORS = [
    'Technology',
    'Healthcare',
    'Financials',
    'Consumer Cyclical',
    'Consumer Defensive',
    'Energy',
    'Industrials',
    'Communication Services',
    'Utilities',
    'Real Estate',
    'Basic Materials',
]

export default function FilterPanel({ filters, onChange, onApply, onReset }) {
    const handle = (key, value) => onChange({ ...filters, [key]: value })

    return (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 space-y-6">
            <h2 className="text-lg font-semibold text-white">Filters</h2>

            {/* Sectors */}
            <div>
                <label className="block text-sm text-gray-400 mb-1">Sector</label>
                <select
                    value={filters.sector || ''}
                    onChange={e => handle('sector', e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                >
                    <option value="">All Sectors</option>
                    {SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
            </div>

            {/* P/E Ratio */}
            <div>
                <label className="block text-sm text-gray-400 mb-1">P/E Ratio</label>
                <div className="flex gap-2">
                    <input
                        type="number"
                        placeholder="Min"
                        value={filters.min_pe || ''}
                        onChange={e => handle('min_pe', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-2 text-sm text-white"
                    />
                    <input
                        type="number"
                        placeholder="Max"
                        value={filters.max_pe || ''}
                        onChange={e => handle('max_pe', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                    />
                </div>
            </div>

            {/* Market Cap */}
            <div>
                <label className="block text-sm text-gray-400 mb-1">Market Cap</label>
                <div className="flex gap-2">
                    <input
                        type="number"
                        placeholder="Min"
                        value={filters.min_market_cap || ''}
                        onChange={e => handle('min_market_cap', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                    />
                    <input
                        type="number"
                        placeholder="Max"
                        value={filters.max_market_cap || ''}
                        onChange={e => handle('max_market_cap', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                    />
                </div>
            </div>

            {/* Beta */}
            <div>
                <label className="block text-sm text-gray-400 mb-1">Beta</label>
                <div className="flex gap-2">
                    <input
                        type="number"
                        placeholder="Min"
                        value={filters.min_beta || ''}
                        onChange={e => handle('min_beta', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                    />
                    <input
                        type="number"
                        placeholder="Max"
                        value={filters.max_beta || ''}
                        onChange={e => handle('max_beta', e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                    />
                </div>
            </div>

            {/* ROE */}
            <div>
                <label className="block text-sm text-gray-400 mb-1">Min ROE (%)</label>
                <input
                    type="number"
                    placeholder="e.g. 15"
                    value={filters.min_roe || ''}
                    onChange={e => handle('min_roe', e.target.value ? e.target.vale / 100 : '')}
                    className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                />
            </div>

            {/* Max Debt/Equity */}
            <div>
                <label className="block text-sm text-gray-400 mb-1">Max Debt / Equity</label>
                <input
                    type="number"
                    placeholder="e.g. 2"
                    value={filters.max_debt_equity || ''}
                    onChange={e => handle('max_debt_equity', e.target.value)}
                    className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm text-white"
                />
            </div>

            {/* Buttons */}
            <div className="flex gap-3 pt-2">
                <button
                    onClick={onApply}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium py-2 rounded transition-colors"
                >
                    Apply
                </button>
                <button
                    onClick={onReset}
                    className="flex-1 bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-medium py-2 rounded transition-colors"
                >
                    Reset
                </button>
            </div>
        </div>
    )
}
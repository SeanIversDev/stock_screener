import { useEffect, useRef } from 'react'
import { createChart, CandlestickSeries } from 'lightweight-charts'

export default function PriceChart({ bars }) {
    const containerRef = useRef(null)

    useEffect(() => {
        if (!bars?.length || !containerRef.current) return

        const chart = createChart(containerRef.current, {
            layout: {
                background: { color: '#111827' },
                textColor: '#9ca3af',
            },
            grid: {
                vertLines: { color: '#1f2937' },
                horzLines: { color: '#1f2937' },
            },
            width: containerRef.current.clientWidth,
            height: 320,
        })

        const series = chart.addSeries(CandlestickSeries, {
            upColor: '#22c55e',
            downColor: '#ef4444',
            borderVisible: false,
            wickUpColor: '#22c55e',
            wickDownColor: '#ef4444',
        })

        series.setData(bars.map(b => ({
            time: b.date,
            open: b.open,
            high: b.high,
            low: b.low,
            close: b.close,
        })))

        chart.timeScale().fitContent()

        const handleResize = () => {
            chart.applyOptions({ width: containerRef.current.clientWidth })
        }
        window.addEventListener('resize', handleResize)

        return () => {
            window.removeEventListener('resize', handleResize)
            chart.remove()
        }
    }, [bars])

    return <div ref={containerRef} />
}
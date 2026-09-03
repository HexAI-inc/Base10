'use client'
import React from 'react'

interface RadarData {
  subject: string
  value: number
  fullMark: number
}

interface RadarChartProps {
  data: RadarData[]
  size?: number
}

export default function RadarChart({ data, size = 300 }: RadarChartProps) {
  const padding = 60
  const center = size / 2
  const radius = (size / 2) - padding
  const angleStep = (Math.PI * 2) / data.length

  // Generate points for the background polygons
  const generatePoints = (factor: number) => {
    return data.map((_, i) => {
      const angle = i * angleStep - Math.PI / 2
      const x = center + radius * factor * Math.cos(angle)
      const y = center + radius * factor * Math.sin(angle)
      return `${x},${y}`
    }).join(' ')
  }

  // Generate points for the data polygon
  const dataPoints = data.map((d, i) => {
    const angle = i * angleStep - Math.PI / 2
    const factor = d.value / d.fullMark
    const x = center + radius * factor * Math.cos(angle)
    const y = center + radius * factor * Math.sin(angle)
    return `${x},${y}`
  }).join(' ')

  return (
    <div className="relative flex items-center justify-center w-full aspect-square max-w-[400px] mx-auto">
      <svg
        viewBox={`0 0 ${size} ${size}`}
        className="w-full h-full overflow-visible"
      >
        {/* Background Polygons */}
        {[0.2, 0.4, 0.6, 0.8, 1].map((factor) => (
          <polygon
            key={factor}
            points={generatePoints(factor)}
            className="fill-none stroke-slate-200 dark:stroke-slate-800 stroke-1"
          />
        ))}

        {/* Axis Lines */}
        {data.map((_, i) => {
          const angle = i * angleStep - Math.PI / 2
          const x = center + radius * Math.cos(angle)
          const y = center + radius * Math.sin(angle)
          return (
            <line
              key={i}
              x1={center}
              y1={center}
              x2={x}
              y2={y}
              className="stroke-slate-200 dark:stroke-slate-800 stroke-1"
            />
          )
        })}

        {/* Data Polygon */}
        <polygon
          points={dataPoints}
          className="fill-emerald-500/20 dark:fill-emerald-500/30 stroke-emerald-500 stroke-2 transition-all duration-1000"
        />

        {/* Data Points */}
        {data.map((d, i) => {
          const angle = i * angleStep - Math.PI / 2
          const factor = d.value / d.fullMark
          const x = center + radius * factor * Math.cos(angle)
          const y = center + radius * factor * Math.sin(angle)
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="4"
              className="fill-emerald-500 stroke-white dark:stroke-slate-950 stroke-2"
            />
          )
        })}

        {/* Labels */}
        {data.map((d, i) => {
          const angle = i * angleStep - Math.PI / 2
          const x = center + (radius + 20) * Math.cos(angle)
          const y = center + (radius + 20) * Math.sin(angle)
          
          // Adjust text anchor based on position
          let textAnchor: "start" | "middle" | "end" = "middle"
          if (Math.cos(angle) > 0.1) textAnchor = "start"
          if (Math.cos(angle) < -0.1) textAnchor = "end"

          return (
            <text
              key={i}
              x={x}
              y={y}
              textAnchor={textAnchor}
              dominantBaseline="middle"
              className="fill-slate-500 dark:fill-slate-400 text-[10px] font-black uppercase tracking-widest"
            >
              {d.subject}
            </text>
          )
        })}
      </svg>
    </div>
  )
}

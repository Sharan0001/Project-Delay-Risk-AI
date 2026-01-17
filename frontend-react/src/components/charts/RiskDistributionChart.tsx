/**
 * Risk Distribution Chart Component - Dark Theme
 * 
 * Displays a donut chart showing High/Medium/Low risk distribution
 * with center label showing total count
 */

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface RiskDistributionChartProps {
    high: number;
    medium: number;
    low: number;
}

// Vibrant colors for dark theme
const COLORS = {
    High: '#F87171',     // Red-400
    Medium: '#FBBF24',   // Amber-400
    Low: '#34D399',      // Emerald-400
};

export function RiskDistributionChart({ high, medium, low }: RiskDistributionChartProps) {
    const data = [
        { name: 'High Risk', value: high, color: COLORS.High },
        { name: 'Medium Risk', value: medium, color: COLORS.Medium },
        { name: 'Low Risk', value: low, color: COLORS.Low },
    ];

    const total = high + medium + low;

    if (total === 0) {
        return (
            <div className="flex items-center justify-center h-64 text-light-400">
                No data available
            </div>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={320}>
            <PieChart margin={{ top: 30, right: 30, bottom: 10, left: 30 }}>
                <Pie
                    data={data}
                    cx="50%"
                    cy="45%"
                    innerRadius={65}
                    outerRadius={95}
                    paddingAngle={3}
                    dataKey="value"
                    label={({ cx, cy, midAngle, outerRadius, percent }) => {
                        if (percent < 0.05) return null;

                        const RADIAN = Math.PI / 180;
                        const radius = outerRadius + 25;
                        const x = cx + radius * Math.cos(-midAngle * RADIAN);
                        const y = cy + radius * Math.sin(-midAngle * RADIAN);

                        return (
                            <text
                                x={x}
                                y={y}
                                fill="#E6EDF3"
                                textAnchor="middle"
                                dominantBaseline="central"
                                fontSize={14}
                                fontWeight={600}
                            >
                                {`${(percent * 100).toFixed(0)}%`}
                            </text>
                        );
                    }}
                    labelLine={false}
                >
                    {data.map((entry, index) => (
                        <Cell
                            key={`cell-${index}`}
                            fill={entry.color}
                            stroke="#1A1E24"
                            strokeWidth={3}
                        />
                    ))}
                </Pie>
                <Tooltip
                    formatter={(value: number) => [
                        `${value.toLocaleString()} tasks`,
                        ''
                    ]}
                    contentStyle={{
                        backgroundColor: '#22272E',
                        border: '1px solid #3D444D',
                        borderRadius: '10px',
                        padding: '10px 14px',
                        color: '#E6EDF3',
                        fontSize: '13px',
                        fontWeight: 500,
                        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.4)',
                    }}
                    itemStyle={{
                        color: '#E6EDF3',
                    }}
                />
                <Legend
                    verticalAlign="bottom"
                    height={40}
                    iconType="circle"
                    iconSize={10}
                    formatter={(value) => (
                        <span style={{ color: '#9CA3AF', fontSize: '13px', fontWeight: 500 }}>
                            {value}
                        </span>
                    )}
                />
            </PieChart>
        </ResponsiveContainer>
    );
}

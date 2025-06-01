"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useHistoricalData } from "@/hooks/api-service";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { AlertOctagon } from "lucide-react";

export function ProductionChart() {
  const { data, loading, error } = useHistoricalData();

  const formatChartData = (histData: any[] | null) => {
    if (!histData) return [];

    return histData.map((entry) => ({
      time: new Date(entry.timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      biogas: entry.biogas_production,
      anomaly: entry.anomaly_probability > 0.5 ? entry.biogas_production : 0,
    }));
  };

  const chartData = formatChartData(data);

  if (loading) {
    return (
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">
            Biogas Production
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500">Loading production data...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">
            Biogas Production
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-64 space-y-2">
            <AlertOctagon className="h-8 w-8 text-red-500" />
            <p className="text-red-500">Failed to load production data</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-white">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-900">
          Biogas Production
        </CardTitle>
        <p className="text-sm text-gray-600">
          Real-time monitoring of biogas output
        </p>
      </CardHeader>
      <CardContent>
        <div className="h-64 md:h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={chartData}
              margin={{ top: 5, right: 5, left: 5, bottom: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 12, fill: "#6b7280" }}
                tickMargin={10}
              />
              <YAxis
                yAxisId="left"
                tick={{ fontSize: 12, fill: "#6b7280" }}
                tickMargin={10}
                label={{
                  value: "m³",
                  angle: -90,
                  position: "insideLeft",
                  offset: 0,
                  fill: "#6b7280",
                  fontSize: 12,
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.95)",
                  border: "1px solid #e5e7eb",
                  borderRadius: "6px",
                  boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
                }}
              />
              <Legend
                verticalAlign="top"
                align="right"
                iconType="circle"
                wrapperStyle={{ paddingBottom: 10 }}
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="biogas"
                name="Biogas Production (m³)"
                stroke="#10b981"
                fill="#10b981"
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="anomaly"
                name="Anomaly Detection"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

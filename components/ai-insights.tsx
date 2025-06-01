"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, AlertCircle, CheckCircle, Brain } from "lucide-react";
import { useSensorData } from "@/hooks/api-service";
import { useEffect, useState } from "react";

type Insight = {
  type: string;
  title: string;
  description: string;
  confidence: number;
  impact: string;
  icon: any;
};

export function AIInsights() {
  const { data, loading } = useSensorData();
  const [insights, setInsights] = useState<Insight[]>([]);

  useEffect(() => {
    if (data) {
      const newInsights = [];

      if (data.ph) {
        if (data.ph < 6.5) {
          newInsights.push({
            type: "optimization",
            title: "pH Level Low",
            description: `Increase pH from ${data.ph?.toFixed(
              1
            )} to optimal range (6.5-8.0) for better biogas production.`,
            confidence: 89,
            impact: "high",
            icon: TrendingUp,
          });
        } else if (data.ph > 8.0) {
          newInsights.push({
            type: "optimization",
            title: "pH Level High",
            description: `Decrease pH from ${data.ph?.toFixed(
              1
            )} to optimal range (6.5-8.0) for better biogas production.`,
            confidence: 91,
            impact: "high",
            icon: TrendingUp,
          });
        } else {
          newInsights.push({
            type: "efficiency",
            title: "Optimal pH Level",
            description: `Current pH (${data.ph?.toFixed(
              1
            )}) is within the optimal range for biogas production.`,
            confidence: 95,
            impact: "low",
            icon: CheckCircle,
          });
        }
      }

      if (data.anomaly_detected) {
        newInsights.push({
          type: "maintenance",
          title: "Anomaly Detected",
          description: `${
            data.anomaly_cause || "Unknown issue"
          } detected. System inspection recommended.`,
          confidence: 88,
          impact: "high",
          icon: AlertCircle,
        });
      }

      if (data.biogas_production) {
        const optimalProduction = 85;
        const difference =
          ((data.biogas_production - optimalProduction) / optimalProduction) *
          100;
        if (difference < -10) {
          newInsights.push({
            type: "optimization",
            title: "Production Optimization",
            description: `Biogas production ${data.biogas_production?.toFixed(
              1
            )}m³ is below target. Consider increasing organic input by 15%.`,
            confidence: 87,
            impact: "medium",
            icon: TrendingUp,
          });
        } else if (difference > 10) {
          newInsights.push({
            type: "efficiency",
            title: "Exceeding Production Targets",
            description: `Biogas production at ${data.biogas_production?.toFixed(
              1
            )}m³ is exceeding targets. System running efficiently.`,
            confidence: 92,
            impact: "low",
            icon: CheckCircle,
          });
        }
      }

      if (newInsights.length === 0) {
        newInsights.push({
          type: "efficiency",
          title: "System Running Optimally",
          description:
            "All parameters within expected ranges. No action needed at this time.",
          confidence: 97,
          impact: "low",
          icon: CheckCircle,
        });
      }

      setInsights(newInsights.slice(0, 3));
    }
  }, [data]);

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "high":
        return "text-red-600";
      case "medium":
        return "text-amber-600";
      case "low":
        return "text-green-600";
      default:
        return "text-gray-600";
    }
  };

  const getIconColor = (type: string) => {
    switch (type) {
      case "optimization":
        return "text-blue-600 bg-blue-50";
      case "maintenance":
        return "text-amber-600 bg-amber-50";
      case "efficiency":
        return "text-green-600 bg-green-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  if (loading) {
    return (
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <p className="text-gray-500">Loading insights...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-white">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold text-gray-900">
          AI Insights
        </CardTitle>
        <div className="flex items-center space-x-2">
          <Brain className="h-4 w-4 text-green-600" />
          <span className="text-sm text-green-600 font-medium">
            Powered by ML
          </span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-5">
          {insights.map((insight, index) => (
            <div key={index} className="flex space-x-4">
              <div
                className={`flex-shrink-0 mt-1 p-2 rounded-lg ${getIconColor(
                  insight.type
                )}`}
              >
                <insight.icon className="h-5 w-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="font-medium text-gray-900">{insight.title}</h4>
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded-full ${getImpactColor(
                      insight.impact
                    )} bg-opacity-10`}
                  >
                    {insight.impact.charAt(0).toUpperCase() +
                      insight.impact.slice(1)}{" "}
                    Impact
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  {insight.description}
                </p>
                <div className="mt-1 flex items-center text-xs text-gray-500">
                  <span>Confidence: </span>
                  <div className="w-16 h-1.5 bg-gray-100 rounded ml-1 mr-1">
                    <div
                      className={`h-full rounded bg-${
                        insight.confidence > 90
                          ? "green"
                          : insight.confidence > 80
                          ? "blue"
                          : "amber"
                      }-500`}
                      style={{ width: `${insight.confidence}%` }}
                    />
                  </div>
                  <span>{insight.confidence}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Check, AlertTriangle, ChevronUp, ChevronDown } from "lucide-react";
import { useSystemStatus, useSensorData } from "@/hooks/api-service";

type SensorData = {
  ph?: number;
  biogas_production?: number;
  anomaly_detected?: boolean;
  system_status?: string;
  timestamp?: string | number;
  anomaly_cause?: string;
};

export function SystemStatus() {
  const { data, loading: dataLoading } = useSensorData() as {
    data: SensorData | null;
    loading: boolean;
  };
  const { status, loading: statusLoading, resetAlarm } = useSystemStatus();

  const handleResetAlarm = async () => {
    await resetAlarm();
  };

  const getStatusItems = () => {
    if (!data) return [];

    return [
      {
        name: "pH Level",
        value: data.ph?.toFixed(1) || "N/A",
        status:
          data.ph && data.ph >= 6.5 && data.ph <= 8.0 ? "normal" : "warning",
      },
      {
        name: "Biogas Production",
        value: `${data.biogas_production?.toFixed(1) || "N/A"} m³`,
        status: "normal",
      },
      {
        name: "System Status",
        value: data.system_status || "Unknown",
        status: data.system_status === "Normal" ? "normal" : "warning",
      },
      {
        name: "Anomaly Detection",
        value: data.anomaly_detected ? "Detected" : "None",
        status: data.anomaly_detected ? "error" : "normal",
      },
    ];
  };

  const statusItems = getStatusItems();

  const getStatusColor = (status: string) => {
    switch (status) {
      case "normal":
        return "text-green-600";
      case "warning":
        return "text-amber-600";
      case "error":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  if (dataLoading || statusLoading) {
    return (
      <Card className="bg-white">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">
            System Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <p className="text-gray-500">Loading system status...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const isSystemHealthy = data && !data.anomaly_detected;

  return (
    <Card className="bg-white">
      <CardHeader>
        <CardTitle className="text-lg font-semibold text-gray-900">
          System Status
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center mb-6">
          <div
            className={`w-12 h-12 rounded-full flex items-center justify-center ${
              isSystemHealthy ? "bg-green-100" : "bg-red-100"
            } mr-4`}
          >
            {isSystemHealthy ? (
              <Check className="w-6 h-6 text-green-600" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-red-600" />
            )}
          </div>
          <div>
            <h3 className="font-medium text-gray-900">
              {isSystemHealthy ? "System Healthy" : "System Warning"}
            </h3>
            <p className="text-sm text-gray-500">
              {isSystemHealthy
                ? "All systems functioning normally"
                : `Issue detected: ${data?.anomaly_cause || "Unknown issue"}`}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          {statusItems.map((item, idx) => (
            <div key={idx} className="flex justify-between items-center">
              <span className="text-gray-600">{item.name}</span>
              <span className={`font-medium ${getStatusColor(item.status)}`}>
                {item.value}
              </span>
            </div>
          ))}
        </div>

        {!isSystemHealthy && (
          <Button
            onClick={handleResetAlarm}
            className="w-full mt-6 bg-red-600 hover:bg-red-700 text-white"
          >
            Reset Alarm
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

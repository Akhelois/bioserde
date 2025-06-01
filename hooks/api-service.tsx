import { useState, useEffect } from "react";
import { apiService } from "@/app/api";

type SensorData = {
  ph: number;
  biogas_production: number;
  timestamp: string;
  anomaly_detected: boolean;
  anomaly_probability: number;
  system_status: string;
  anomaly_cause?: string;
};

type SystemStatus = {
  status: string;
  last_updated: string;
  anomaly_detected: boolean;
  anomaly_cause: string;
};

type HistoricalData = SensorData[];

export function useSensorData(refreshInterval = 10000) {
  const [data, setData] = useState<SensorData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiService.getSensorData();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    const intervalId = setInterval(fetchData, refreshInterval);

    return () => clearInterval(intervalId);
  }, [refreshInterval]);

  return { data, loading, error };
}

export function useHistoricalData() {
  const [data, setData] = useState<HistoricalData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await apiService.getHistoricalData();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, loading, error };
}

export function useSystemStatus(refreshInterval = 15000) {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        const result = await apiService.getSystemStatus();
        setStatus(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : String(err));
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();

    const intervalId = setInterval(fetchStatus, refreshInterval);
    return () => clearInterval(intervalId);
  }, [refreshInterval]);

  const resetAlarm = async () => {
    try {
      await apiService.resetAlarm();
      const result = await apiService.getSystemStatus();
      setStatus(result);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
      return false;
    }
  };

  return { status, loading, error, resetAlarm };
}

const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  async get(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API GET error:', error);
      throw error;
    }
  }

  async post(endpoint, data = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API POST error:', error);
      throw error;
    }
  }

  async getSensorData() {
    return this.get('/sensor-data');
  }

  async getHistoricalData() {
    return this.get('/historical-data');
  }

  async predict(ph, biogasProduction) {
    return this.post('/predict', {
      ph: ph,
      biogas_production: biogasProduction
    });
  }

  async resetAlarm() {
    return this.post('/reset-alarm');
  }

  async getSystemStatus() {
    return this.get('/system-status');
  }
}

export const apiService = new ApiService();
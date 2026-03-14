import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // Flask backend URL

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

export default api;

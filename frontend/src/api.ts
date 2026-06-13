import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
});

export const getProjectState = async () => {
  const response = await api.get('/state');
  return response.data;
};

export const initializeProject = async (name: string) => {
  const response = await api.post(`/initialize?project_name=${encodeURIComponent(name)}`);
  return response.data;
};

export const generatePlan = async (request: string) => {
  const response = await api.post(`/plan?user_request=${encodeURIComponent(request)}`);
  return response.data;
};

export const executeTasks = async () => {
  const response = await api.post('/execute');
  return response.data;
};

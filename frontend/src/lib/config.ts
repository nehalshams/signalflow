// Base URL for the Django REST API. Override with VITE_API_BASE_URL in a
// .env file (see .env.example).
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

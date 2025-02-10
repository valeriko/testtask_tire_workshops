import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_APP_BACKEND_URL + "/api";

export const fetchWorkshops = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/workshops/`);
    return response.data;
  } catch (error) {
    console.error("Error fetching workshops:", error);
    return [];
  }
};

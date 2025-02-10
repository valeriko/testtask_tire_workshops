<template>
  <div class="workshops-container">
    <div class="header">
      <router-link to="/" class="back-button">Back to booking</router-link>
    </div>

    <h2>Available tire workshops</h2>

    <div class="actions-row">
      <button @click="openAddModal" class="add-button">Add workshop</button>
    </div>

    <div class="table-container">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>City</th>
            <th>Address</th>
            <th>Vehicle types</th>
            <th>URLs and Methods</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="workshop in workshops" :key="workshop.id_workshop" :class="{ inactive: !workshop.is_active }">
            <td>{{ workshop.id_workshop }}</td>
            <td>{{ workshop.name }}</td>
            <td>{{ workshop.city }}</td>
            <td>{{ workshop.address }}</td>
            <td>{{ workshop.vehicle_types.replaceAll(',', ', ') }}</td>
            <td class="urls">
              <div><strong>Available times:</strong> {{ workshop.url_available_times }}</div>
              <div><strong>Booking ({{ workshop.booking_http_method }}):</strong> {{ workshop.url_booking }}</div>
            </td>
            <td class="actions">
              <button @click="openEditModal(workshop)" class="edit-button">Edit</button>
              <button @click="toggleActive(workshop)" :class="['toggle-button', workshop.is_active ? 'active' : 'inactive']">
                {{ workshop.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Workshop Modal (Add/Edit) -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <h3>{{ editingWorkshop ? 'Edit Workshop' : 'Add Workshop' }}</h3>
        <form @submit.prevent="saveWorkshop">
          <div class="form-group">
            <label>Name:</label>
            <input v-model="workshopForm.name" required>
          </div>
          <div class="form-group">
            <label>City:</label>
            <input v-model="workshopForm.city" required>
          </div>
          <div class="form-group">
            <label>Address:</label>
            <input v-model="workshopForm.address" required>
          </div>
          <div class="form-group">
            <label>Vehicle types:</label>
            <div class="checkbox-group">
              <label v-for="type in vehicleTypes" :key="type">
                <input
                  type="checkbox"
                  :value="type"
                  v-model="workshopForm.vehicle_types"
                />
                {{ type }}
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>URL of available times:</label>
            <input v-model="workshopForm.url_available_times" required>
          </div>
          <div class="form-group">
            <label>Predefined response type:</label>
            <select v-model="workshopForm.response_type" required>
              <option v-for="type in responseTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>URL of booking:</label>
            <input v-model="workshopForm.url_booking" required>
          </div>
          <div class="form-group">
            <label>HTTP method for booking:</label>
            <select v-model="workshopForm.booking_http_method" required>
              <option v-for="method in bookingHttpMethods" :key="method" :value="method">
                {{ method }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Booking body template:</label>
            <input v-model="workshopForm.booking_body" placeholder="{contact_info}" required>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-button" @click="closeModal">Cancel</button>
            <button type="submit" class="save-button">Save</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL, fetchWorkshops } from "../services";

export default {
  name: "WorkshopsTable",
  data() {
    return {
      workshops: [],
      vehicleTypes: [], // Dynamic vehicle types from backend
      responseTypes: [],
      bookingHttpMethods: [],
      showModal: false,
      editingWorkshop: null,
      workshopForm: {
        name: '',
        city: '',
        address: '',
        vehicle_types: [], // Array to handle selected vehicle types
        url_available_times: '',
        response_type: '',
        url_booking: '',
        booking_http_method: '',
        booking_body: '',
      }
    };
  },
  async created() {
    await Promise.all([
      this.loadWorkshops(),
      this.loadFilters()
    ]);
  },
  methods: {
    async loadWorkshops() {
      try {
        this.workshops = await fetchWorkshops();
      } catch (error) {
        console.error("Failed to load workshops data:", error);
      }
    },
    async loadFilters() {
      try {
        const response = await fetch(`${API_BASE_URL}/workshops/filters`);
        if (!response.ok) throw new Error('Failed to load filters');
        const data = await response.json();

        this.vehicleTypes = data.vehicle_types; // Populate vehicle types dynamically
        this.responseTypes = data.response_types;
        this.bookingHttpMethods = data.booking_http_methods;

        // Set defaults for form inputs
        this.workshopForm.response_type = this.responseTypes[0];
        this.workshopForm.booking_http_method = this.bookingHttpMethods[0];
      } catch (error) {
        console.error("Failed to load filters:", error);
      }
    },
    openAddModal() {
      this.editingWorkshop = null;
      this.resetForm();
      this.showModal = true;
    },
    openEditModal(workshop) {
      this.editingWorkshop = workshop;
      this.workshopForm = {
        name: workshop.name,
        city: workshop.city,
        address: workshop.address,
        vehicle_types: workshop.vehicle_types
          ? workshop.vehicle_types.split(',').map(type => type.trim()) // Convert string to array
          : [], // Default to empty array if undefined
        url_available_times: workshop.url_available_times,
        response_type: workshop.response_type,
        url_booking: workshop.url_booking,
        booking_http_method: workshop.booking_http_method,
        booking_body: workshop.booking_body,
      };
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.editingWorkshop = null;
      this.resetForm();
    },
    resetForm() {
      this.workshopForm = {
        name: '',
        city: '',
        address: '',
        vehicle_types: [], // Reset to empty array
        url_available_times: '',
        response_type: this.responseTypes[0] || '',
        url_booking: '',
        booking_http_method: this.bookingHttpMethods[0] || '',
        booking_body: '',
      };
    },
    async saveWorkshop() {
      try {
        const workshopData = {
          name: this.workshopForm.name,
          city: this.workshopForm.city,
          address: this.workshopForm.address,
          vehicle_types: Array.isArray(this.workshopForm.vehicle_types)
            ? this.workshopForm.vehicle_types.join(',') // Convert array to comma-separated string
            : '', // Default to empty string if not an array
          url_available_times: this.workshopForm.url_available_times,
          response_type: this.workshopForm.response_type,
          url_booking: this.workshopForm.url_booking,
          booking_http_method: this.workshopForm.booking_http_method,
          booking_body: this.workshopForm.booking_body,
        };

        const url = `${API_BASE_URL}/workshops/` + (this.editingWorkshop ? this.editingWorkshop.id_workshop : '');
        const method = this.editingWorkshop ? 'PUT' : 'POST';

        const response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json', },
          body: JSON.stringify(workshopData),
        });

        if (!response.ok) throw new Error('Failed to save workshop');

        await this.loadWorkshops();
        this.closeModal();
      } catch (error) {
        console.error('Error saving workshop:', error);
      }
    },
    async toggleActive(workshop) {
      try {
        const response = await fetch(`${API_BASE_URL}/workshops/${workshop.id_workshop}/toggle-active`, {
          method: 'POST'
        });

        if (!response.ok) throw new Error('Failed to toggle workshop status');

        await this.loadWorkshops();
      } catch (error) {
        console.error('Error toggling workshop status:', error);
      }
    }
  }
};
</script>

<style scoped>
.workshops-container {
  padding: 20px;
  width: 98%;
}

.header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
  font-size: 24px;
}

.actions-row {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 20px;
}

.back-button {
  display: inline-block;
  padding: 8px 16px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-decoration: none;
  color: #333;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.3s, opacity 0.3s;
  cursor: pointer;
}

.back-button:hover {
  background-color: #e9ecef;
  opacity: 0.9;
}

.add-button {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.table-container {
  width: 100%;
  overflow-x: auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
}

tr:hover {
  background-color: #f8f9fa;
}

tr.inactive {
  opacity: 0.4;
  color: #999;
}

.urls {
  font-size: 0.9em;
}

.urls div {
  margin-bottom: 4px;
}

.actions {
  display: flex;
  gap: 8px;
}

.edit-button, .toggle-button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.edit-button {
  background-color: #007bff;
  color: white;
}

.toggle-button {
  background-color: #6c757d;
  color: white;
}

.toggle-button.active {
  background-color: #dc3545;
}

.toggle-button.inactive {
  background-color: #28a745;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 25px;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.checkbox-group {
  display: flex;
  gap: 20px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button, .save-button {
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-button {
  background: #f8f9fa;
  border: 1px solid #ddd;
}

.save-button {
  background: #28a745;
  color: white;
  border: none;
}

.back-button:hover,
.add-button:hover,
.edit-button:hover,
.toggle-button:hover,
.save-button:hover {
  opacity: 0.9;
}
</style>

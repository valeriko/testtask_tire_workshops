<template>
  <div class="available-times-container">
    <h2>You pick the time, we change the tires</h2>

    <div class="filter-section">
      <div class="filters-row">
        <div class="filter-group date-group">
          <label for="date-from">From:</label>
          <input id="date-from" type="date" v-model="filters.date_from" class="filter-item" placeholder="From">
        </div>
        <div class="filter-group date-group">
          <label for="date-to">To:</label>
          <input id="date-to" type="date" v-model="filters.date_to" class="filter-item" placeholder="To">
        </div>
        <select v-model="filters.vehicle_types" class="filter-item">
          <option value="">All vehicle types</option>
          <option v-for="type in vehicleTypes" :key="type" :value="type">{{ type }}</option>
        </select>
        <select v-model="filters.cities" class="filter-item">
          <option value="">All cities</option>
          <option v-for="city in cities" :key="city" :value="city">{{ city }}</option>
        </select>
        <select v-model="filters.workshop_name" class="filter-item">
          <option value="">All tire workshops</option>
          <option v-for="name in workshopNames" :key="name" :value="name">{{ name }}</option>
        </select>
      </div>

      <button @click="searchAvailableTimes" class="search-button" :disabled="isLoading">
        <span v-if="!isLoading">Show available times</span>
        <div v-else class="spinner"></div>
      </button>
    </div>

    <div v-if="groupedTimeslots.length > 0" class="timeslots-section">
      <div v-for="dayGroup in groupedTimeslots" :key="dayGroup.date" class="day-group">
        <h3>{{ formatDate(dayGroup.date) }}</h3>
        <div class="slots-grid">
          <div v-for="slot in dayGroup.slots"
               :key="slot.id_slot"
               class="time-slot-card"
               @click="openBooking(slot)">
            <div class="card-header">
              <div class="time">{{ formatTime(slot.slot_datetime) }}</div>
              <div class="vehicle-types">{{ getWorkshopInfo(slot.id_workshop).vehicle_types.replaceAll(',', ', ') }}</div>
            </div>
            <div class="details" v-if="getWorkshopInfo(slot.id_workshop)">
              <div class="location">{{ getWorkshopInfo(slot.id_workshop).address }}, {{ getWorkshopInfo(slot.id_workshop).city }}</div>
              <div class="workshop-name">{{ getWorkshopInfo(slot.id_workshop).name }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="timeslots.length === 0 && searchPerformed && !isLoading" class="no-results fade-in">
      No available time slots found matching your criteria.
    </div>

    <BookingModal
      v-if="selectedSlot"
      :show="!!selectedSlot"
      :slot="selectedSlot"
      :workshop="getWorkshopInfo(selectedSlot?.id_workshop)"
      @close="selectedSlot = null"
    />
  </div>
</template>

<script>
import BookingModal from './BookingModal.vue';
import { API_BASE_URL } from '../services';

export default {
  components: {
    BookingModal
  },
  data() {
    return {
      filters: {
        date_from: '',
        date_to: '',
        vehicle_types: '',
        cities: '',
        workshop_name: ''
      },
      vehicleTypes: [],
      cities: [],
      workshopNames: [],
      timeslots: [],
      workshops: [],
      searchPerformed: false,
      isLoading: false,
      autoSubmit: false,
      selectedSlot: null
    };
  },
  computed: {
    groupedTimeslots() {
      const groups = {};
      this.timeslots.forEach(slot => {
        const date = new Date(slot.slot_datetime).toISOString().split('T')[0];
        if (!groups[date]) {
          groups[date] = {
            date: date,
            slots: []
          };
        }
        groups[date].slots.push(slot);
      });

      return Object.values(groups).sort((a, b) => a.date.localeCompare(b.date));
    }
  },
  async created() {
    try {
      const [filtersResponse, workshopsResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/workshops/filters`),
        fetch(`${API_BASE_URL}/workshops/`)
      ]);

      const filtersData = await filtersResponse.json();
      this.vehicleTypes = filtersData.vehicle_types;
      this.cities = filtersData.cities;
      this.workshopNames = filtersData.workshop_names;
      this.filters.date_from = filtersData.default_date_from;
      this.filters.date_to = filtersData.default_date_to;

      this.workshops = await workshopsResponse.json();
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  },
  watch: {
    filters: {
      deep: true,
      handler(newVal) {
        if (this.autoSubmit) {
          this.searchAvailableTimes();
        }
      }
    }
  },
  methods: {
    getWorkshopInfo(id) {
      return this.workshops.find(w => w.id_workshop === id);
    },
    openBooking(slot) {
      console.log('Opening booking for slot:', slot);
      this.selectedSlot = slot;
    },
    async searchAvailableTimes() {
      if (this.isLoading) return;

      this.autoSubmit = true;
      this.isLoading = true;
      this.timeslots = [];
      this.searchPerformed = true;

      const queryParams = new URLSearchParams();
      if (this.filters.date_from) queryParams.append('date_from', this.filters.date_from);
      if (this.filters.date_to) queryParams.append('date_to', this.filters.date_to);
      if (this.filters.vehicle_types) queryParams.append('vehicle_types', this.filters.vehicle_types);
      if (this.filters.cities) queryParams.append('cities', this.filters.cities);
      if (this.filters.workshop_name) queryParams.append('workshop_name', this.filters.workshop_name);

      try {
        const response = await fetch(`${API_BASE_URL}/booking/available-times?${queryParams.toString()}`);
        if (!response.ok) throw new Error('Network response was not ok');
        this.timeslots = await response.json();
      } catch (error) {
        console.error('Error fetching available times:', error);
      } finally {
        this.isLoading = false;
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
    },
    formatTime(datetime) {
      return new Date(datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  }
};
</script>

<style scoped>
.available-times-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.filter-section {
  background-color: #f4f4f4;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.filters-row {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.filter-item {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 0;
}

.search-button {
  width: 37%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 42px;
  font-weight: bold;
  font-size: 120%;
}

.search-button:hover {
  background-color: #0056b3;
}

.search-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

.day-group {
  margin-bottom: 30px;
}

.day-group h3 {
  margin-bottom: 15px;
  border-bottom: 2px solid #eee;
  padding-bottom: 5px;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.time-slot-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.time-slot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  background-color: snow;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.time {
  font-size: 1.2em;
  font-weight: bold;
  color: #007bff;
}

.vehicle-types {
  font-size: 0.85em;
  color: #666;
}

.details {
  font-size: 0.9em;
  color: #666;
}

.location {
  margin-bottom: 5px;
}

.workshop-name {
  font-weight: 600;
  color: #333;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.no-results {
  text-align: center;
  color: #666;
  margin-top: 20px;
}

.filters-row {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  align-items: flex-end; /* Ensures alignment to the bottom of the line */
}

.filter-group {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.filter-item {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 0;
}

.date-group label {
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

select.filter-item,
input.filter-item {
  height: 34px;
}

</style>

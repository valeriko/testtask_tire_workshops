<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal">
      <h3>Confirm booking</h3>

      <div class="booking-details">
        <div class="time">{{ formatTime(slot.slot_datetime) }}</div>
        <div class="workshop-info">
          <div>{{ workshop.address }}, {{ workshop.city }}</div>
          <div class="workshop-name">{{ workshop.name }}</div>
          <div class="vehicle-types">{{ workshop.vehicle_types.replaceAll(',', ', ') }}</div>
        </div>
      </div>

      <div class="phone-input">
        <label>Your phone number:</label>
        <input
          type="tel"
          v-model="phoneNumber"
          placeholder="+372 5123 4567"
          :class="{ 'error': showError }"
        >
        <div v-if="showError" class="error-message">Please enter a valid phone number</div>
      </div>

      <div class="actions">
        <button class="cancel-button" @click="$emit('close')">Cancel</button>
        <button class="book-button" @click="handleBook" :disabled="isLoading">
          <span v-if="!isLoading">Book</span>
          <div v-else class="spinner"></div>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from '../services';

export default {
  props: {
    show: Boolean,
    slot: Object,
    workshop: Object
  },
  data() {
    return {
      phoneNumber: '',
      showError: false,
      isLoading: false
    }
  },
  methods: {
    formatTime(datetime) {
      return new Date(datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    validatePhone() {
      const phoneRegex = /^\+?\d{7,15}$/;
      return phoneRegex.test(this.phoneNumber.replace(/\s/g, ''));
    },
    mounted() {
      console.log('Modal mounted with props:', {
        show: this.show,
        slot: this.slot,
        workshop: this.workshop
      });
    },
    sendSMS(phoneNumber, message) {
      // check if it is a mobile phone number
      // use Messente
      console.log(`Sent SMS to ${phoneNumber}: ${message}`);
    },
    async handleBook() {
      if (!this.validatePhone()) {
        this.showError = true;
        return;
      }

      this.showError = false;
      this.isLoading = true;

      try {
        const customerPhone = this.phoneNumber.replace(/\s/g, '');

        const queryParams = new URLSearchParams({
          id_workshop: this.slot.id_workshop.toString(),
          customer_phone: customerPhone
        }).toString();

        const response = await fetch(
          `${API_BASE_URL}/booking/reserve/${this.slot.id_slot}?${queryParams}`,
          { method: 'POST' }
        );

        const result = await response.json();

        if (response.ok && result.status_code === 200) {
          this.$router.push({
            name: 'booking-confirmation',
            query: {
              success: true,
              message: result.message,
              datetime: this.slot.slot_datetime,
              workshop: this.workshop.name,
              city: this.workshop.city,
              address: this.workshop.address
            }
          });
          // Extract and format date and time
          const slotDateTime = new Date(this.slot.slot_datetime);
          const slotDate = `${slotDateTime.getDate().toString().padStart(2, '0')}.${(slotDateTime.getMonth() + 1).toString().padStart(2, '0')}.${slotDateTime.getFullYear()}`;
          const slotTime = `${slotDateTime.getHours().toString().padStart(2, '0')}:${slotDateTime.getMinutes().toString().padStart(2, '0')}`;

          this.sendSMS(customerPhone, `Your tire change time has been booked for ${this.workshop.name}, ${this.workshop.address}, ${this.workshop.city}, on ${slotDate} at ${slotTime}.`);
        } else {
          this.$router.push({
            name: 'booking-confirmation',
            query: {
              success: false,
              message: result.message
            }
          });
        }
      } catch (error) {
        this.$router.push({
          name: 'booking-confirmation',
          params: {
            success: false,
            message: 'Network error occurred'
          }
        });
      } finally {
        this.isLoading = false;
        this.$emit('close');
      }
    }
  }
}
</script>

<style scoped>
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
  max-width: 500px;
}

.booking-details {
  margin: 20px 0;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 4px;
}

.time {
  font-size: 1.4em;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 10px;
}

.workshop-info {
  line-height: 1.5;
}

.workshop-name {
  font-weight: 600;
  margin-bottom: 5px;
}

.phone-input {
  margin: 20px 0;
}

.phone-input label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.phone-input input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.phone-input input.error {
  border-color: #dc3545;
}

.error-message {
  color: #dc3545;
  font-size: 0.875em;
  margin-top: 5px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-button, .book-button {
  padding: 8px 20px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
}

.cancel-button {
  background: #f8f9fa;
  border: 1px solid #ddd;
}

.book-button {
  background: #007bff;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 80px;
}

.book-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>

<template>
  <div class="confirmation-container">
    <div class="confirmation-card" :class="{ 'success': success, 'error': !success }">
      <div v-if="success">
        <h2>Booking confirmed!</h2>
        <div class="details">
          <p>Your tire change is scheduled for {{ formatDateTime(datetime) }}</p>
          <p>at {{ workshop }}</p>
          <p>Address: {{ address }}, {{ city }} </p>
        </div>
      </div>
      <div v-else>
        <h2>Booking failed</h2>
        <p class="message">{{ message }}</p>
      </div>

      <router-link to="/" class="back-button">Back to search</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BookingConfirmation',
  computed: {
    success() {
      return this.$route.query.success === 'true'
    },
    message() {
      return this.$route.query.message
    },
    datetime() {
      return this.$route.query.datetime
    },
    workshop() {
      return this.$route.query.workshop
    },
    city() {
      return this.$route.query.city
    },
    address() {
      return this.$route.query.address
    }
  },
  methods: {
    formatDateTime(datetime) {
      if (!datetime) return '';
      return new Date(datetime).toLocaleString('en-GB', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  }
}
</script>

<style scoped>
.confirmation-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.confirmation-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.success {
  border-top: 4px solid #28a745;
}

.error {
  border-top: 4px solid #dc3545;
}

.details {
  margin: 20px 0;
  line-height: 1.6;
}

.message {
  margin: 20px 0;
  font-weight: 500;
}

.back-button {
  display: inline-block;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.back-button:hover {
  background-color: #0056b3;
}
</style>

import { createRouter, createWebHistory } from 'vue-router';

import AvailableTimes from '../components/AvailableTimes.vue';
import WorkshopsTable from '../components/WorkshopsTable.vue';
import BookingConfirmation from '../components/BookingConfirmation.vue';

const routes = [
    { path: '/', component: AvailableTimes },
    { path: '/configure-workshops', component: WorkshopsTable },
    {
      path: '/booking-confirmation',
      name: 'booking-confirmation',
      component: BookingConfirmation,
      props: true
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;

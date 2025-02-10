<template>
  <div>
    <div class="header">
      <router-link to="/configure-workshops" class="config-button" v-if="$route.path === '/'">
        Configure workshops
      </router-link>
    </div>
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style>
.header {
  position: absolute;
  top: 20px;
  right: 20px;
}

.config-button {
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

.config-button:hover {
  background-color: #e9ecef;
  opacity: 0.9;
}
</style>

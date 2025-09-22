<template>
  <div class="removed-feature">
    <div class="feature-notice">
      <h2>功能已移除</h2>
      <p>Agent管理功能已不再可用。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// Agent管理功能已移除
</script>

<style scoped>
.removed-feature {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background-color: var(--bg-color);
}

.feature-notice {
  text-align: center;
  padding: 2rem;
  background-color: var(--card-bg);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.feature-notice h2 {
  color: var(--text-color);
  margin-bottom: 1rem;
}

.feature-notice p {
  color: var(--text-secondary);
}
</style>
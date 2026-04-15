<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4">
    <div class="max-w-2xl mx-auto text-center">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-6">
        关于
      </h1>
      <p class="text-gray-600 dark:text-gray-300 mb-4">
        这是一个基于 Vite + Vue 3 + TypeScript 的前端项目。
      </p>
      <p class="text-gray-600 dark:text-gray-300">
        技术栈：Vue Router、Pinia、Tailwind CSS、ESLint、Prettier。
      </p>
      <nav class="mt-8 flex justify-center gap-4">
        <router-link
          to="/"
          class="text-indigo-600 dark:text-indigo-400 hover:underline"
          active-class="font-semibold"
        >
          首页
        </router-link>
        <router-link
          to="/about"
          class="text-indigo-600 dark:text-indigo-400 hover:underline"
          active-class="font-semibold"
        >
          关于
        </router-link>
      </nav>
    </div>
  </div>
</template>

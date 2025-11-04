// frontend/ecosystem.config.js
// PM2 configuration for the Next.js frontend.
// Ensures NODE_ENV is set to production for optimized builds and runtime behavior.

module.exports = {
  apps: [
    {
      name: "music-frontend",
      script: "npm",
      args: "start",
      env: {
        NODE_ENV: "production",
        AUTH_DEBUG: "true",
      },
    },
  ],
};

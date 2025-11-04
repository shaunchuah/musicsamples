// frontend/ecosystem.config.js
// PM2 configuration for the Next.js frontend.
// Ensures NODE_ENV is set to production for optimized builds and runtime behavior.

module.exports = {
  apps: [
    {
      name: "music-frontend",
      cwd: __dirname,
      script: "pnpm",
      args: "start",
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};

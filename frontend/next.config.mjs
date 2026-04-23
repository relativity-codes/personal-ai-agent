/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  webpack: (config, { dev }) => {
    // Dev-only: stale webpack filesystem cache can reference missing numeric chunks (e.g. ./948.js)
    // after refactors or interrupted compiles—especially when loading the internal _not-found route.
    if (dev) {
      config.cache = false;
    }
    return config;
  },
};

export default nextConfig;

const withMDX = require("@next/mdx")();

/** @type {import('next').NextConfig} */
const nextConfig = withMDX({
  reactStrictMode: true,
  swcMinify: true,
});

module.exports = nextConfig;

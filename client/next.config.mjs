/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "rubicstorage.blob.core.windows.net",
      },
    ],
  },
};

export default nextConfig;

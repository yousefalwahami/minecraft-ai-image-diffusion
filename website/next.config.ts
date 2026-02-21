import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  rewrites: async () => {
    return [
      {
        source: '/:path*',
        destination: process.env.NODE_ENV === 'development' 
          ? 'http://127.0.0.1:5328/:path*' // Your local Python port
          : '/api/', // In production, Vercel handles this automatically
      },
    ];
  },
};

export default nextConfig;

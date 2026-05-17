const nextConfig: import('next').NextConfig = {
  output: 'export',
  // Optional: Disable image optimization if using Next.js Image component with static export
  images: {
    unoptimized: true,
  },
};

export default nextConfig;

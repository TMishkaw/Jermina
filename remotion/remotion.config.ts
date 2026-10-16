/**
 * Remotion Configuration file.
 * Optimizes video rendering pipeline for multi-core CPU and GPU acceleration.
 */

import { Config } from "@remotion/cli/config";

// 1. Encoding Speed: veryfast preset speeds up x264 video encoding by ~2.5x
Config.setX264Preset("veryfast");

// 2. Webpack Bundle Caching: eliminates re-bundling from scratch on every run
Config.setCachingEnabled(true);

// 3. Concurrency: utilize 6 parallel browser render threads on Intel i7-8850H (6C/12T)
Config.setConcurrency(6);

// 4. Pixel Format: fast standard 4:2:0 YUV for maximal hardware/player compatibility
Config.setPixelFormat("yuv420p");

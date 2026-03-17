#!/bin/bash
# 虾老板 WebGL 强制启动脚本

pkill -9 chromium
pkill -9 Xvfb
sleep 2

# 启动 Xvfb
Xvfb :99 -screen 0 1280x720x24 &
sleep 2

# 设置环境变量
export DISPLAY=:99
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_GL_VERSION_OVERRIDE=4.0
export GALLIUM_DRIVER=llvmpipe

# 启动 Chromium 带 WebGL 强制标志
nohup chromium \
    --remote-debugging-port=9222 \
    --user-data-dir=/tmp/chromium-webgl-final \
    --enable-webgl \
    --enable-webgl2-compute-context \
    --enable-accelerated-2d-canvas \
    --enable-gpu-rasterization \
    --enable-zero-copy \
    --use-gl=desktop \
    --disable-gpu \
    --disable-gpu-process \
    --disable-gpu-compositing \
    --disable-software-rasterizer \
    --disable-gpu-sandbox \
    --disable-gpu-driver-bug-workarounds \
    --ignore-gpu-blocklist \
    --override-gl-version="4.0" \
    --force-device-scale-factor=1 \
    http://localhost:8888/dashboard/index-3d.html \
    > /tmp/chromium-final-attempt.log 2>&1 &

echo "🦐 虾老板 Chromium 已启动！"
echo "等待 10 秒..."
sleep 10

# 检查 WebGL 状态
curl -s http://localhost:9222/json/list | head -20

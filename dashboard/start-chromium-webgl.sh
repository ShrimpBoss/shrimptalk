#!/bin/bash
# 虾老板 WebGL 启动脚本

# 杀死现有 Chromium 进程
pkill -9 chromium 2>/dev/null
sleep 2

# 设置环境变量启用软件渲染
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_GL_VERSION_OVERRIDE=4.0
export GALLIUM_DRIVER=llvmpipe

# 启动 Chromium 带 WebGL 支持
chromium \
    --remote-debugging-port=9222 \
    --user-data-dir=/tmp/chromium-webgl-profile \
    --enable-webgl \
    --enable-webgl2-compute-context \
    --use-gl=swiftshader \
    --disable-gpu \
    --disable-gpu-process \
    --disable-software-rasterizer \
    --disable-gpu-sandbox \
    --disable-gpu-compositing \
    --ignore-gpu-blocklist \
    http://localhost:8888/dashboard/index-3d.html &

echo "🦐 虾老板 Chromium 已启动！"
echo "访问地址：http://localhost:8888/dashboard/index-3d.html"
echo "调试端口：9222"

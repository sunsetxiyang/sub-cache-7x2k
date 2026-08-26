#!/bin/bash
# 合并两台机器的订阅文件（美西机器执行）
# 输入: A/links.txt A/clash-proxies.txt B/links.txt B/clash-proxies.txt
# 输出: links.txt v2ray(base64) clash.yaml
# B 停机标记（B/.stopped 存在时）→ 只合并 A
set -e
cd "$(dirname "$0")"

# B 是否停机（标记文件存在则排除 B）
INCLUDE_B="yes"
if [ -f B/.stopped ]; then
  INCLUDE_B="no"
  echo "B 停机中（检测到 B/.stopped），仅合并美西 A"
fi

# 1. 合并明文链接
if [ "$INCLUDE_B" = "yes" ]; then
  cat A/links.txt B/links.txt 2>/dev/null | grep -v '^$' > links.txt
else
  cat A/links.txt 2>/dev/null | grep -v '^$' > links.txt
fi
echo "合并链接数: $(wc -l < links.txt)"

# 2. base64 订阅
base64 -w0 links.txt > v2ray

# 3. clash.yaml
cat > clash.yaml <<'EOF'
mixed-port: 7890
allow-lan: false
mode: rule
log-level: info

EOF

echo "proxies:" >> clash.yaml
cat A/clash-proxies.txt 2>/dev/null >> clash.yaml || true
if [ "$INCLUDE_B" = "yes" ]; then
  cat B/clash-proxies.txt 2>/dev/null >> clash.yaml || true
fi

# 提取所有节点名（供 proxy-groups 使用）
NAMES=$(grep -oP '^  - name: \K.*' clash.yaml || true)
GROUP_PROXIES=""
while IFS= read -r n; do
  [ -n "$n" ] && GROUP_PROXIES="${GROUP_PROXIES}      - ${n}"$'\n'
done <<< "$NAMES"

cat >> clash.yaml <<EOF

proxy-groups:
  - name: PROXY
    type: select
    proxies:
${GROUP_PROXIES}      - AUTO
  - name: AUTO
    type: url-test
    url: http://www.gstatic.com/generate_204
    interval: 300
    proxies:
${GROUP_PROXIES}

rules:
  - GEOIP,CN,DIRECT
  - MATCH,PROXY
EOF

echo "生成完成: links.txt v2ray clash.yaml"

#!/bin/bash
clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║              MONITORING STACK - FINAL STATUS                ║"
echo "╚══════════════════════════════════════════════════════════════╝"

echo -e "\n📦 ALL CONTAINERS:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n🎯 PROMETHEUS TARGETS:"
curl -s http://localhost:9090/api/v1/targets | python3 -c "
import sys, json
data = json.load(sys.stdin)
for t in data['data']['activeTargets']:
    s = '✅' if t['health'] == 'up' else '❌'
    j = t['labels'].get('job','?')
    f = t['labels'].get('framework','')
    print(f'{s} {j:20s} {f}')
"

echo -e "\n🌐 API HEALTH & LATENCY:"
for f in express fastapi spring dotnet; do
    s=$(curl -s "http://localhost:9090/api/v1/query?query=probe_success{framework=\"$f\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['result'][0]['value'][1])" 2>/dev/null)
    l=$(curl -s "http://localhost:9090/api/v1/query?query=probe_duration_seconds{framework=\"$f\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['result'][0]['value'][1][:6])" 2>/dev/null)
    [ "$s" = "1" ] && echo "✅ $f: ${l}s" || echo "❌ $f: DOWN"
done

echo -e "\n💻 EC2 RESOURCES:"
cpu=$(curl -s 'http://localhost:9090/api/v1/query?query=100-(avg(rate(node_cpu_seconds_total{mode="idle"}[1m]))*100)' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['result'][0]['value'][1][:5])" 2>/dev/null)
mem=$(curl -s 'http://localhost:9090/api/v1/query?query=(1-(node_memory_MemAvailable_bytes/node_memory_MemTotal_bytes))*100' | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['result'][0]['value'][1][:5])" 2>/dev/null)
echo "CPU: ${cpu}% | Memory: ${mem}%"

echo -e "\n📊 ACCESS POINTS:"
echo "Grafana:       http://localhost:3000 (admin/admin)"
echo "Prometheus:    http://localhost:9090"
echo "Alertmanager:  http://localhost:9093"
echo "cAdvisor:      http://localhost:8081"
echo "API Gateway:   http://localhost:8080"
echo ""
echo "API Endpoints:"
echo "  Express:  http://localhost:8080/api/express/employees"
echo "  FastAPI:  http://localhost:8080/api/employees"
echo "  Spring:   http://localhost:8080/api/spring/employees"
echo "  DotNet:   http://localhost:8080/api/dotnet/employees"

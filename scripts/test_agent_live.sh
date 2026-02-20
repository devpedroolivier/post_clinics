#!/bin/bash
# POST Clinics - Live Agent Verification
API="http://localhost:8005/webhook/zapi"

echo "=== TESTE 1: Saudacao ==="
curl -s -X POST $API -H "Content-Type: application/json" \
  -d '{"phone":"5500000000001","text":{"message":"Oi, boa tarde!"},"messageId":"test_greet_001","fromMe":false,"isGroup":false}' | python3 -m json.tool
echo ""

sleep 3

echo "=== TESTE 2: Listar Servicos ==="
curl -s -X POST $API -H "Content-Type: application/json" \
  -d '{"phone":"5500000000001","text":{"message":"Quais servicos voces oferecem?"},"messageId":"test_services_002","fromMe":false,"isGroup":false}' | python3 -m json.tool
echo ""

sleep 3

echo "=== TESTE 3: Disponibilidade ==="
curl -s -X POST $API -H "Content-Type: application/json" \
  -d '{"phone":"5500000000001","text":{"message":"Tem horario amanha para clinica geral?"},"messageId":"test_avail_003","fromMe":false,"isGroup":false}' | python3 -m json.tool
echo ""

sleep 3

echo "=== TESTE 4: Agendar ==="
curl -s -X POST $API -H "Content-Type: application/json" \
  -d '{"phone":"5500000000001","text":{"message":"Pode marcar as 10:00 por favor. Meu nome e Maria Silva."},"messageId":"test_schedule_004","fromMe":false,"isGroup":false}' | python3 -m json.tool
echo ""

sleep 3

echo "=== TESTE 5: Confirmar ==="
curl -s -X POST $API -H "Content-Type: application/json" \
  -d '{"phone":"5500000000001","text":{"message":"Confirmo minha presenca"},"messageId":"test_confirm_005","fromMe":false,"isGroup":false}' | python3 -m json.tool
echo ""

sleep 3

echo "=== TESTE 6: Reagendar ==="
curl -s -X POST $API -H "Content-Type: application/json" \
  -d '{"phone":"5500000000001","text":{"message":"Preciso remarcar para as 14:00"},"messageId":"test_reschedule_006","fromMe":false,"isGroup":false}' | python3 -m json.tool
echo ""

sleep 3

echo "=== TESTE 7: Cancelar ==="
curl -s -X POST $API -H "Content-Type: application/json" \
  -d '{"phone":"5500000000001","text":{"message":"Quero cancelar minha consulta"},"messageId":"test_cancel_007","fromMe":false,"isGroup":false}' | python3 -m json.tool
echo ""

echo "=== TESTES CONCLUIDOS ==="

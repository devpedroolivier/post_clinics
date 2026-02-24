#!/bin/bash
# POST Clinics - Live Agent Verification
API="http://localhost:8005/webhook/zapi"
WEBHOOK_SIGNATURE_SECRET="${WEBHOOK_SIGNATURE_SECRET:-change_me_webhook_secret}"
WEBHOOK_SIGNATURE_HEADER="${WEBHOOK_SIGNATURE_HEADER:-X-Webhook-Signature}"

sign_payload() {
  local payload="$1"
  PAYLOAD="$payload" SECRET="$WEBHOOK_SIGNATURE_SECRET" python3 -c "import os,hmac,hashlib;print(hmac.new(os.environ['SECRET'].encode(), os.environ['PAYLOAD'].encode(), hashlib.sha256).hexdigest())"
}

post_payload() {
  local payload="$1"
  local sig
  sig=$(sign_payload "$payload")
  curl -s -X POST "$API" \
    -H "Content-Type: application/json" \
    -H "$WEBHOOK_SIGNATURE_HEADER: sha256=$sig" \
    --data "$payload" | python3 -m json.tool
}

echo "=== TESTE 1: Saudacao ==="
post_payload '{"phone":"5500000000001","text":{"message":"Oi, boa tarde!"},"messageId":"test_greet_001","fromMe":false,"isGroup":false}'
echo ""

sleep 3

echo "=== TESTE 2: Listar Servicos ==="
post_payload '{"phone":"5500000000001","text":{"message":"Quais servicos voces oferecem?"},"messageId":"test_services_002","fromMe":false,"isGroup":false}'
echo ""

sleep 3

echo "=== TESTE 3: Disponibilidade ==="
post_payload '{"phone":"5500000000001","text":{"message":"Tem horario amanha para clinica geral?"},"messageId":"test_avail_003","fromMe":false,"isGroup":false}'
echo ""

sleep 3

echo "=== TESTE 4: Agendar ==="
post_payload '{"phone":"5500000000001","text":{"message":"Pode marcar as 10:00 por favor. Meu nome e Maria Silva."},"messageId":"test_schedule_004","fromMe":false,"isGroup":false}'
echo ""

sleep 3

echo "=== TESTE 5: Confirmar ==="
post_payload '{"phone":"5500000000001","text":{"message":"Confirmo minha presenca"},"messageId":"test_confirm_005","fromMe":false,"isGroup":false}'
echo ""

sleep 3

echo "=== TESTE 6: Reagendar ==="
post_payload '{"phone":"5500000000001","text":{"message":"Preciso remarcar para as 14:00"},"messageId":"test_reschedule_006","fromMe":false,"isGroup":false}'
echo ""

sleep 3

echo "=== TESTE 7: Cancelar ==="
post_payload '{"phone":"5500000000001","text":{"message":"Quero cancelar minha consulta"},"messageId":"test_cancel_007","fromMe":false,"isGroup":false}'
echo ""

echo "=== TESTES CONCLUIDOS ==="

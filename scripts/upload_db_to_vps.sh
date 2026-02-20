#!/bin/bash

# Este script envia com segurança os bancos de dados locais para o seu VPS na Hostinger.
# Certifique-se de preencher as variáveis abaixo antes de executar.

# Configuração do VPS
VPS_USER="root" # ou seu usuário ssh
VPS_HOST="191.101.235.185" # IP do VPS na Hostinger (do print)
VPS_PORT="22" # Porta SSH
VPS_DIR="/path/to/your/project/on/vps" # Mude para o caminho real no VPS!

# Diretório local do banco (onde este script está rodando)
LOCAL_DATA_DIR="$(dirname "$0")/../data"

echo "============================================="
echo "   Sincronizando Banco de Dados para VPS"
echo "============================================="
echo "Origem: $LOCAL_DATA_DIR"
echo "Destino: $VPS_USER@$VPS_HOST:$VPS_DIR/data/"
echo "============================================="

# Confirmação
read -p "Deseja continuar? (s/N): " confirm
if [[ ! "$confirm" =~ ^[sS]$ ]]; then
    echo "Operação cancelada."
    exit 1
fi

echo "Iniciando upload usando rsync..."

# rsnyc para transferir os arquivos mantendo as permissões e sincronizando apenas o que mudou
# -a: archive mode (recursivo, preserva links, permissões, tempos, grupos, owners)
# -v: verbose
# -z: compress file data during the transfer
# -e "ssh -p": usar ssh com a porta certa
rsync -avz -e "ssh -p $VPS_PORT" "$LOCAL_DATA_DIR/" "$VPS_USER@$VPS_HOST:$VPS_DIR/data/"

if [ $? -eq 0 ]; then
    echo "✅ Subida do banco de dados concluída com sucesso!"
    echo "Lembre-se de verificar se os arquivos .db estão lá e se as permissões no servidor estão corretas."
else
    echo "❌ Erro ao enviar os dados. Verifique a conexão SSH e as credenciais."
fi

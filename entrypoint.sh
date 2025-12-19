#!/bin/bash
set -e

# Iniciar o servidor de webhooks em background
echo "Iniciando Webhook Server..."
python scripts/run_webhooks.py &

# Iniciar o scheduler em background
echo "Iniciando Scheduler..."
python scripts/run_scheduler.py &

# Aguarda qualquer processo sair
wait -n

# Sai com o status do processo que terminou primeiro
exit $?

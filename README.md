# Marketplace e Serviço de Notificações
### Marketplace: 
Plataforma de compra e venda com catálogo, carrinho e pedidos. 
### Serviço de Notificações: 
Recebe eventos do Marketplace e entrega aos usuários em tempo real.
### Integração: 
Marketplace emite eventos assíncronos (novo pedido, produto esgotado) para o Serviço de
Notificações via gRPC. Circuit Breaker garante que o Marketplace continue funcionando mesmo se
Notificações cair.

# Marketplace
**Equipe:** Arthur Lobo, Antônio Monteiro, Guilherme Viana, José Vitor.
* **Comunicação:**
gRPC com métodos ListProducts, PlaceOrder, UpdateStock. Cliente nunca gerencia sockets.
* **N-Camadas:**
Apresentação (CLI ou frontend web via FastAPI gateway) → Servidor gRPC (lógica de negócios)
→ PostgreSQL (persistência).
* **Concorrência:** 
asyncio com grpc.aio, múltiplos compradores em paralelo.
* **Tolerância a Falhas:** 
Circuit Breaker para chamadas ao Serviço de Notificações (3 falhas → circuito abre).
Retry com backoff no cliente.
* **Sincronização:** 
Redlock no Redis por product_id ao confirmar pedido, evitando overselling.
* **Descoberta de Serviços:** 
Registra-se no Consul. Consulta Consul para descobrir endereço do Serviço de
Notificações.
* **Consistência Eventual:** 
Duas instâncias com replicação assíncrona. Status pending/complete nos metadados.

# Serviço de Notificações
**Equipe:** Antônio Nunes, Arthur Ricardo, Guido Xenofonte, João Manoel.
* **Comunicação:** gRPC para receber eventos (EmitEvent) e streaming para entregar ao cliente (Subscribe).
WebSocket via gateway FastAPI para o browser.
* **N-Camadas:** Painel web → Gateway FastAPI (WebSocket) → Servidor gRPC → PostgreSQL.
* **Concorrência:** asyncio.Queue por usuário conectado. Cada mensagem de qualquer emissor é colocada na fila
do usuário correto.
* **Tolerância a Falhas:** Idempotência via event_id — mesmo evento reenviado não duplica a notificação.
* **Sincronização:** Relógios de Lamport para ordenar eventos de múltiplas fontes em ordem causal.
* **Descoberta de Serviços:** Registra-se no Consul para ser descoberto pelo Marketplace.
* **Consistência Eventual:** Duas instâncias com propagação assíncrona de eventos.

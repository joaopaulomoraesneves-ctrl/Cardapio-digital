DELÍCIA DIGITAL v5 — DEMO OPERACIONAL

Arquivos:
- index.html
- manifest.webmanifest
- sw.js

Como testar:
1. Coloque os três arquivos na mesma pasta.
2. Para testar PWA e service worker, rode um servidor local:
   python -m http.server 8000
3. Acesse:
   http://localhost:8000
4. Painel admin:
   http://localhost:8000/#admin

Senha do admin:
admin123

Novidades da v5:
- Controle de estoque real no painel.
- Produto sem estoque fica indisponível no cardápio.
- Bloqueio de adição ao carrinho quando ultrapassa estoque.
- Baixa de estoque quando o pedido é aceito/preparado/pronto/saiu/finalizado.
- Devolução de estoque se pedido já baixado for cancelado.
- Tela da cozinha para tablet/monitor.
- Impressão de pedido e impressão dos pedidos abertos da cozinha.
- Relatórios operacionais.
- Exportação CSV de pedidos, produtos e clientes.
- Histórico de clientes por WhatsApp.
- Botão para repetir último pedido de cliente.
- Aba de assinatura/cobrança planejada para integração futura com Asaas.
- Base mais próxima de uma operação real antes da migração para Supabase + Asaas.

Observação importante:
Esta versão ainda é uma DEMO LOCAL e usa localStorage. Ela é boa para apresentação comercial, validação com clientes e testes de fluxo. Para vender como SaaS real, o próximo passo é migrar para backend, banco de dados, login real e cobrança integrada.

Próxima etapa recomendada:
- Next.js + Supabase para multi-restaurante, banco, login e storage.
- Asaas para cobrança mensal dos estabelecimentos.
- Webhooks para ativar/bloquear assinatura automaticamente.

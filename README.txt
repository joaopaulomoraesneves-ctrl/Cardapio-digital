DELÍCIA DIGITAL v3 - DEMO COMERCIAL

Arquivos:
- index.html: sistema completo com cardápio público, carrinho, checkout, painel admin e pedidos.
- manifest.webmanifest: configuração PWA.
- sw.js: service worker para cache/offline básico.

Como testar:
1. Mantenha os 3 arquivos na mesma pasta.
2. Abra o index.html no navegador.
3. Para testar melhor o PWA, rode em servidor local:
   python -m http.server 8000
   Depois acesse: http://localhost:8000

Painel admin:
- Acesse pelo link no rodapé "Acesso do estabelecimento" ou abra index.html#admin.
- Senha da demo: admin123

Novidades da v3:
- Interface pública mais limpa.
- Admin separado por rota/hash.
- Header com capa, logo, status, tempo e pedido mínimo.
- Promoções e destaques no lugar dos cards institucionais.
- Produtos com tags, promoção, estoque, serve/unidade e sugestões.
- Checkout em etapas.
- Pedido salvo no painel antes do envio ao WhatsApp.
- Status de pedidos em estilo operacional.
- QR Code por mesa/comanda.
- Configurações de negócio: segmento, cor, logo, capa, WhatsApp, Pix, taxas e pedido mínimo.
- Modo mais adequado para restaurantes, lanchonetes, bares e distribuidoras.

Observação:
Esta versão ainda é uma demo local baseada em localStorage. Para venda em escala como SaaS real, o próximo passo é migrar para backend, banco de dados, autenticação real e multi-restaurante.

# VideoDown.io - Baixador de Vídeos Universal

Aplicação web completa desenvolvida com **FastAPI** e **yt-dlp** para baixar vídeos de qualquer tamanho e de diversas plataformas (YouTube, TikTok, Instagram, Twitter/X, Vimeo, Facebook, links diretos MP4/WebM/MKV, etc.).

---

## 🚀 Como Executar

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.8+** instalado em seu sistema.

### 2. Instalar as Dependências
No terminal, execute o comando para instalar as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

> **Nota:** As dependências principais são:
> - `fastapi` & `uvicorn`: Framework web assíncrono de alta performance.
> - `yt-dlp`: Engine para extração de vídeos de centenas de sites.
> - `httpx`: Cliente HTTP assíncrono para streaming de download em alta velocidade.
> - `pydantic`: Validação de esquemas e dados.

### 3. Iniciar o Servidor
Execute o seguinte comando na raiz do projeto:

```bash
uvicorn app:app --reload
```

O servidor iniciará em `http://127.0.0.1:8000`. Acesse esse endereço no seu navegador!

---

## ✨ Funcionalidades

- **Download Ultra-Rápido (CDN):** Redirecionamento HTTP 307 direto para os servidores CDN do vídeo, garantindo a máxima velocidade da sua conexão de internet.
- **Download Proxy Assíncrono:** Transmissão de vídeo via servidor em chunks de 4MB com suporte a requisições HTTP `Range` (resume/multithread).
- **Formatos e Qualidades:** Exibição de opções de resolução (1080p, 720p, 480p, MP3/Áudio).
- **Cópia de Link Direto:** Facilidade para copiar a URL original de mídia para gerenciadores de download externos (Ex: IDM, wget, curl).
- **Interface Moderna:** Design responsivo no estilo Dark Mode feito com Tailwind CSS.

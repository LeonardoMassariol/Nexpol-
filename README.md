🧠 NexPol — Advanced Polarization Analysis for Reddit Data
🇧🇷 Português | 🇺🇸 English | 🇪🇸 Español

📚 Índice | Index | Índice
🇧🇷 Português
🇺🇸 English
🇪🇸 Español

🇧🇷 Português
🚀 Visão Geral
O NexPol é uma aplicação em Python para coletar posts do Reddit, analisar sentimento e calcular polarização de discussões.

Fluxo principal:

Coleta posts de um subreddit via API do Reddit (PRAW)
Limpa texto e calcula sentimento com VADER (NLTK)
Calcula polarização simples e avançada
Exibe resultados na GUI (gráficos, tabela, nuvem de palavras, metadados)
Exporta relatório consolidado em DOCX
🧩 Funcionalidades
📥 Coleta de posts por subreddit
🔎 Filtro opcional por tema/palavra-chave
💬 Análise de sentimento: compound, pos, neg, neu
📊 Polarização simples (variância)
📈 Polarização avançada (variância, extremismo, entropia, gini)
🎨 Interface com tema claro/escuro
🌐 Interface em Português, Inglês e Espanhol
❓ Botão e menu de ajuda traduzidos conforme idioma selecionado
🪵 Logs internacionalizados (pt/en/es)
📝 Exportação de relatório em DOCX
🔐 Autenticação local de usuários (SQLite)
📐 Fórmula de Polarização Avançada
Variância: 40%
Extremismo: 30%
(1 - Entropia normalizada): 20%
Gini: 10%
score_final = variancia*0.4 + extremismo*0.3 + (1-entropia)*0.2 + gini*0.1
Classificações: very_low, low, moderate, high, very_high.

🏗️ Estrutura do Projeto
NexPol/
|- gui.py
|- main.py
|- .env                  # não versionado
|- usuarios.db           # banco local de autenticação
|- nexpol/
|  |- __init__.py
|  |- i18n_logs.py
|  |- core/
|  |  |- __init__.py
|  |  |- environment.py
|  |  |- reddit_client.py
|  |  |- processor.py
|  |- ui/
|     |- __init__.py
|     |- auth.py
|     |- charts.py
|     |- controls.py
|     |- export_service.py
|     |- main_window.py
|     |- models.py
|     |- styles.py
|     |- workers.py
|- README.md
|- .gitignore
⚙️ Requisitos e Instalação
Python 3.11+
Credenciais da API do Reddit
Dependências:

PyQt5
praw
pandas
numpy
scipy
nltk
matplotlib
seaborn
wordcloud
python-docx
python-dotenv
git clone https://github.com/seu-usuario/nexpol.git
cd nexpol

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

pip install pyqt5 praw pandas numpy scipy nltk matplotlib seaborn wordcloud python-docx python-dotenv
🔐 Configuração da API do Reddit
Crie um arquivo .env na raiz:

REDDIT_CLIENT_ID=seu_client_id
REDDIT_CLIENT_SECRET=seu_client_secret
REDDIT_USER_AGENT=nexpol_app
Crie o app em: https://www.reddit.com/prefs/apps (tipo script).

▶️ Execução
Interface gráfica:

python gui.py
Uso programático:

from nexpol.core.processor import RedditDataProcessor

processor = RedditDataProcessor()
ok = processor.process_data(subreddit="brasil", sample_size=100)

if ok:
    processor.generate_report("relatorio.txt")
🌐 Idioma
A aplicação permite alternar entre Português, Inglês e Espanhol durante a sessão
O botão de ajuda e o conteúdo do diálogo de ajuda acompanham o idioma selecionado
Logs principais também acompanham o idioma selecionado
O idioma não é persistido entre sessões

🇺🇸 English
🚀 Overview
NexPol is a Python application to collect Reddit posts, run sentiment analysis, and calculate discussion polarization.

Main flow:

Fetch posts from a subreddit using Reddit API (PRAW)
Clean text and run sentiment analysis with VADER (NLTK)
Compute simple and advanced polarization
Display results in GUI (charts, table, word cloud, metadata)
Export consolidated DOCX report
🧩 Features
📥 Subreddit post collection
🔎 Optional topic/keyword filtering
💬 Sentiment analysis: compound, pos, neg, neu
📊 Simple polarization (variance)
📈 Advanced polarization (variance, extremism, entropy, gini)
🎨 Light/dark theme
🌐 UI in Portuguese, English, and Spanish
❓ Help button and help dialog translated based on selected language
🪵 Internationalized logs (pt/en/es)
📝 DOCX report export
🔐 Local user authentication (SQLite)
📐 Advanced Polarization Formula
Variance: 40%
Extremism: 30%
(1 - normalized entropy): 20%
Gini: 10%
score_final = variance*0.4 + extremism*0.3 + (1-entropy)*0.2 + gini*0.1
Levels: very_low, low, moderate, high, very_high.

🏗️ Project Structure
NexPol/
|- gui.py
|- main.py
|- .env                  # not versioned
|- usuarios.db           # local authentication database
|- nexpol/
|  |- __init__.py
|  |- i18n_logs.py
|  |- core/
|  |  |- __init__.py
|  |  |- environment.py
|  |  |- reddit_client.py
|  |  |- processor.py
|  |- ui/
|     |- __init__.py
|     |- auth.py
|     |- charts.py
|     |- controls.py
|     |- export_service.py
|     |- main_window.py
|     |- models.py
|     |- styles.py
|     |- workers.py
|- README.md
|- .gitignore
⚙️ Requirements and Setup
Python 3.11+
Reddit API credentials
git clone https://github.com/seu-usuario/nexpol.git
cd nexpol

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

pip install pyqt5 praw pandas numpy scipy nltk matplotlib seaborn wordcloud python-docx python-dotenv
🔐 Reddit API Configuration
Create a .env file at project root:

REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=nexpol_app
Create your app at: https://www.reddit.com/prefs/apps (script type).

▶️ Run
GUI:

python gui.py
Programmatic usage:

from nexpol.core.processor import RedditDataProcessor

processor = RedditDataProcessor()
ok = processor.process_data(subreddit="python", sample_size=100)

if ok:
    processor.generate_report("report.txt")
🌐 Language Notes
Language can be switched during the session
Help button and help dialog follow selected UI language
Main internal logs follow selected language
Language is not persisted between sessions

🇪🇸 Español
🚀 Resumen
NexPol es una aplicación en Python para recopilar publicaciones de Reddit, analizar sentimiento y calcular polarización de discusiones.

Flujo principal:

Obtiene publicaciones de un subreddit usando la API de Reddit (PRAW)
Limpia texto y aplica análisis de sentimiento con VADER (NLTK)
Calcula polarización simple y avanzada
Muestra resultados en la GUI (gráficos, tabla, nube de palabras, metadatos)
Exporta informe consolidado en DOCX
🧩 Funcionalidades
📥 Recolección de publicaciones por subreddit
🔎 Filtro opcional por tema/palabra clave
💬 Análisis de sentimiento: compound, pos, neg, neu
📊 Polarización simple (varianza)
📈 Polarización avanzada (varianza, extremismo, entropía, gini)
🎨 Tema claro/oscuro
🌐 Interfaz en Portugués, Inglés y Español
❓ Botón y menú de ayuda traducidos según idioma seleccionado
🪵 Logs internacionalizados (pt/en/es)
📝 Exportación de informe en DOCX
🔐 Autenticación local de usuarios (SQLite)
📐 Fórmula de Polarización Avanzada
Varianza: 40%
Extremismo: 30%
(1 - entropía normalizada): 20%
Gini: 10%
score_final = varianza*0.4 + extremismo*0.3 + (1-entropia)*0.2 + gini*0.1
Niveles: very_low, low, moderate, high, very_high.

🏗️ Estructura del Proyecto
NexPol/
|- gui.py
|- main.py
|- .env                  # no versionado
|- usuarios.db           # base de datos local de autenticación
|- nexpol/
|  |- __init__.py
|  |- i18n_logs.py
|  |- core/
|  |  |- __init__.py
|  |  |- environment.py
|  |  |- reddit_client.py
|  |  |- processor.py
|  |- ui/
|     |- __init__.py
|     |- auth.py
|     |- charts.py
|     |- controls.py
|     |- export_service.py
|     |- main_window.py
|     |- models.py
|     |- styles.py
|     |- workers.py
|- README.md
|- .gitignore
⚙️ Requisitos e Instalación
Python 3.11+
Credenciales de la API de Reddit
git clone https://github.com/seu-usuario/nexpol.git
cd nexpol

python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

pip install pyqt5 praw pandas numpy scipy nltk matplotlib seaborn wordcloud python-docx python-dotenv
🔐 Configuración de la API de Reddit
Crea un archivo .env en la raíz:

REDDIT_CLIENT_ID=tu_client_id
REDDIT_CLIENT_SECRET=tu_client_secret
REDDIT_USER_AGENT=nexpol_app
Crea la app en: https://www.reddit.com/prefs/apps (tipo script).

▶️ Ejecución
Interfaz gráfica:

python gui.py
Uso programático:

from nexpol.core.processor import RedditDataProcessor

processor = RedditDataProcessor()
ok = processor.process_data(subreddit="brasil", sample_size=100)

if ok:
    processor.generate_report("reporte.txt")
🌐 Idioma
El idioma se puede cambiar durante la sesión
El botón de ayuda y el contenido del diálogo siguen el idioma seleccionado
Los logs principales también siguen el idioma seleccionado
El idioma no se guarda entre sesiones
👨‍💻 Autores
Andrius Nazario
Braian Leão
Leonardo S. Ruschel
Leonardo Massariol
📌 Licencia
Uso educacional y analítico. Ajustar según la licencia oficial que el equipo quiera adoptar (MIT, Apache-2.0, etc.).

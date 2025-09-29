import sys
import os
import json
import pandas as pd
import pyqtgraph as pg
import numpy as np
import math

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QProgressBar,
                             QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QFileDialog, QGroupBox, QFormLayout, QSpinBox, QSplitter, QInputDialog, QDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor

# Importar sua classe existente
from main import RedditDataProcessor

class AnalysisThread(QThread):
    """Thread para executar a análise em segundo plano"""
    progress_signal = pyqtSignal(str, int)
    finished_signal = pyqtSignal(bool, dict, pd.DataFrame)
    error_signal = pyqtSignal(str)
    
    def __init__(self, processor, subreddit, sample_size):
        super().__init__()
        self.processor = processor
        self.subreddit = subreddit
        self.sample_size = sample_size
    
    def run(self):
        try:
            self.progress_signal.emit("Iniciando análise...", 10)
            
            # Processar dados
            success = self.processor.process_data(self.subreddit, self.sample_size)
            
            if success:
                self.progress_signal.emit("Gerando visualizações...", 70)
                
                self.progress_signal.emit("Análise concluída!", 100)
                self.finished_signal.emit(True, self.processor.stats, self.processor.processed_data)
            else:
                self.error_signal.emit("Falha no processamento dos dados")
                
        except Exception as e:
            self.error_signal.emit(f"Erro durante a análise: {str(e)}")

class WelcomeOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        from PyQt5.QtWidgets import QSizePolicy
        overlay_layout = QVBoxLayout(self)
        overlay_layout.setAlignment(Qt.AlignCenter)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(0)
        label = QLabel('Bem-vindo ao NexPol')
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont('Arial', 14, QFont.Bold))
        label.setStyleSheet('color: #1976D2; background: transparent;')
        overlay_layout.addStretch(1)
        overlay_layout.addWidget(label, alignment=Qt.AlignCenter)
        overlay_layout.addStretch(1)
        self.setMinimumSize(400, 120)
        self.resize(400, 120)
        self.center_on_parent()
    def center_on_parent(self):
        if self.parent():
            parent_geom = self.parent().geometry()
            x = parent_geom.x() + (parent_geom.width() - self.width()) // 2
            y = parent_geom.y() + (parent_geom.height() - self.height()) // 2
            self.move(x, y)

class AuthWindow(QDialog):
    def load_users(self):
        users_file = os.path.join(os.path.dirname(__file__), 'users.json')
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except Exception:
                    return {}
        return {}
    def show_register(self):
        self.clear()
        self.show_logo()
        label = QLabel('Cadastro')
        label.setFont(QFont('Arial', 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        self.user = QLineEdit()
        self.user.setPlaceholderText('nome.sobrenome')
        self.layout.addWidget(self.user)
        self.pwd = QLineEdit()
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd.setPlaceholderText('senha')
        self.layout.addWidget(self.pwd)
        btn_reg = QPushButton('Registrar')
        btn_reg.clicked.connect(self.register)
        self.layout.addWidget(btn_reg)
        btn_back = QPushButton('Voltar')
        btn_back.clicked.connect(self.show_login)
        self.layout.addWidget(btn_back)
    def login(self):
        user = self.user.text()
        pwd = self.pwd.text()
        users = self.load_users()
        if user in users and users[user]['password'] == pwd:
            self.accepted = True
            self.close()
        else:
            QMessageBox.critical(self, 'Erro', 'Usuário ou senha inválidos')
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Acesso NEXPOL')
        self.setFixedSize(340, 420)
        self.layout = QVBoxLayout(self)
        self.show_login()

    def clear(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget: widget.setParent(None)

    def show_logo(self):
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), 'logo.jpg')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaledToWidth(180, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText('NEXPOL')
            logo_label.setFont(QFont('Arial', 24, QFont.Bold))
            logo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(logo_label)

    def show_login(self):
        self.clear()
        self.show_logo()
        label = QLabel('Login')
        label.setFont(QFont('Arial', 16, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        self.user = QLineEdit()
        self.user.setPlaceholderText('nome.sobrenome')
        self.layout.addWidget(self.user)
        self.pwd = QLineEdit()
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd.setPlaceholderText('senha')
        self.layout.addWidget(self.pwd)
        btn_login = QPushButton('Entrar')
        btn_login.clicked.connect(self.login)
        self.layout.addWidget(btn_login)
        btn_reg = QPushButton('Cadastrar')
        btn_reg.clicked.connect(self.show_register)
        self.layout.addWidget(btn_reg)

    def register(self):
        user, pwd = self.user.text(), self.pwd.text()
        if '.' not in user or not pwd:
            QMessageBox.critical(self, 'Erro', 'Formato: nome.sobrenome e senha obrigatória')
            return
        users = self.load_users()
        if user in users:
            QMessageBox.critical(self, 'Erro', 'Usuário já existe')
            return
        users[user] = {'password': pwd}
        self.save_users(users)
        QMessageBox.information(self, 'Sucesso', 'Cadastro realizado!')
        self.show_login()

    def recover(self):
        user, ok = QInputDialog.getText(self, 'Recuperar', 'Digite nome.sobrenome:')
        if not ok: return
        users = self.load_users()
        if user in users:
            QMessageBox.information(self, 'Recuperação', f'Sua senha: {users[user]["password"]}')
        else:
            QMessageBox.critical(self, 'Erro', 'Usuário não encontrado')
    def save_users(self, users):
        users_file = os.path.join(os.path.dirname(__file__), 'users.json')
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

class RedditAnalyzerGUI(QMainWindow):
    def display_results(self):
        if self.current_stats:
            score = self.current_stats.get('polarization_score', None)
            if score is not None:
                self.polarization_label.setText(f"Polarização: {score:.4f}")
            else:
                self.polarization_label.setText("Polarização: N/A")
        else:
            self.polarization_label.setText("Polarização: N/A")

        if hasattr(self, 'stats_widget'):
            layout = self.stats_widget.layout()
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
            if self.current_stats:
                stats_text = (
                    f"<b>Subreddit:</b> {self.current_stats.get('subreddit', '')}<br>"
                    f"<b>Total de posts:</b> {self.current_stats.get('total_posts', '')}<br>"
                    f"<b>Média de score:</b> {self.current_stats.get('avg_score', ''):.2f}<br>"
                    f"<b>Média de comentários:</b> {self.current_stats.get('avg_comments', ''):.2f}<br>"
                    f"<b>Média de sentimento:</b> {self.current_stats.get('avg_sentiment', ''):.4f}<br>"
                    f"<b>Posts positivos:</b> {self.current_stats.get('positive_posts', '')}<br>"
                    f"<b>Posts negativos:</b> {self.current_stats.get('negative_posts', '')}<br>"
                    f"<b>Posts neutros:</b> {self.current_stats.get('neutral_posts', '')}<br>"
                )
                label = QLabel(stats_text)
                label.setTextFormat(Qt.RichText)
                layout.addWidget(label)
            else:
                layout.addWidget(QLabel("Nenhuma estatística disponível."))

        columns_to_show = ['id', 'title', 'author', 'score', 'created_utc', 'sentiment', 'sentimento']
        if hasattr(self, 'data_table') and self.current_data is not None and not self.current_data.empty:
            df = self.current_data.copy()
            idioma = self.language_combo.currentText() if hasattr(self, 'language_combo') else 'Português'
            t = self.get_translations()[idioma]
            if 'sentiment_compound' in df.columns:
                def sentimento_label(val, t=t):
                    if val > 0.05:
                        return t.get('positive', 'Positivo')
                    elif val < -0.05:
                        return t.get('negative', 'Negativo')
                    else:
                        return t.get('neutral', 'Neutro')
                df['sentimento'] = df['sentiment_compound'].apply(sentimento_label)
            df = df[[col for col in columns_to_show if col in df.columns]]
            self.data_table.setRowCount(len(df))
            self.data_table.setColumnCount(len(df.columns))
            header_map = {
                'id': t.get('id', 'id'),
                'title': t.get('title', 'title'),
                'author': t.get('author', 'author'),
                'score': t.get('score', 'score'),
                'created_utc': t.get('created_utc', 'created_utc'),
                'sentiment': t.get('sentiment', 'sentiment'),
                'sentimento': t.get('sentimento', 'Sentimento')
            }
            headers = [header_map.get(col, col) for col in df.columns]
            self.data_table.setHorizontalHeaderLabels(headers)
            for i, row in df.iterrows():
                for j, value in enumerate(row):
                    self.data_table.setItem(i, j, QTableWidgetItem(str(value)))
        else:
            if hasattr(self, 'data_table'):
                self.data_table.setRowCount(0)
                self.data_table.setColumnCount(0)
        
        if hasattr(self, 'graph_plot_widget'):
            self.display_graph()

    def clear_all(self):
        """Limpa todos os campos, estatísticas, dados e gráficos da interface, resetando a visualização."""
        self.subreddit_input.clear()
        self.update_graph_section_visibility()
        self.current_stats = None
        self.current_data = pd.DataFrame()
        self.clear_graph()
        self.polarization_label.setText("Polarização: N/A")
        self.data_table.setRowCount(0)
        self.export_btn.setEnabled(False)
        self.tabs.setTabText(0, self.get_translations()['Português']['statistics'])
        self.tabs.setTabText(1, self.get_translations()['Português']['data_table'])
        self.tabs.setTabText(2, "Gráfico")
        self.update_interface_language()

    def get_translations(self):
        return {
            'Português': {
                'polarization': 'Polarização',
                'config_section': 'Configuração de Análise',
                'subreddit': 'Subreddit',
                'sample_size': 'Tamanho da Amostra',
                'analyze': 'Iniciar Análise',
                'clear': 'Limpar',
                'export': 'Exportar Dados',
                'statistics': 'Estatísticas',
                'data_table': 'Dados',
                'language': 'Idioma da Interface',
                'status_ready': 'Pronto para analisar',
                'status_done': 'Análise concluída!',
                'status_fail': 'Falha na análise.',
                'no_posts': 'Nenhum post encontrado no idioma selecionado.',
                'comments': 'Comentários',
                'sentiment': 'Sentimento',
                'date': 'Data',
                'title': 'Título',
                'author': 'Autor',
                'score': 'Score',
                'positive': 'Positivo',
                'negative': 'Negativo',
                'neutral': 'Neutro',
                'sentimento': 'Sentimento',
                'graph_bar': 'Barras',
                'graph_score_sentiment': 'Score vs. Sentimento',
                'graph_pie': 'Setores (Pizza)'
            },
            'Inglês': {
                'polarization': 'Polarization',
                'config_section': 'Analysis Configuration',
                'subreddit': 'Subreddit',
                'sample_size': 'Sample Size',
                'analyze': 'Start Analysis',
                'clear': 'Clear',
                'export': 'Export Data',
                'statistics': 'Statistics',
                'data_table': 'Data',
                'language': 'Interface Language',
                'status_ready': 'Ready for analysis',
                'status_done': 'Analysis completed!',
                'status_fail': 'Analysis failed.',
                'no_posts': 'No posts found in the selected language.',
                'comments': 'Comments',
                'sentiment': 'Sentiment',
                'date': 'Date',
                'title': 'Title',
                'author': 'Score',
                'score': 'Score',
                'positive': 'Positive',
                'negative': 'Negative',
                'neutral': 'Neutral',
                'sentimento': 'Sentiment',
                'graph_bar': 'Bars',
                'graph_score_sentiment': 'Score vs. Sentiment',
                'graph_pie': 'Pie Chart'
            },
            'Espanhol': {
                'polarization': 'Polarización',
                'config_section': 'Configuración de Análisis',
                'subreddit': 'Subreddit',
                'sample_size': 'Tamaño de Muestra',
                'analyze': 'Iniciar Análisis',
                'clear': 'Limpiar',
                'export': 'Exportar Datos',
                'statistics': 'Estadísticas',
                'data_table': 'Datos',
                'language': 'Idioma de la Interfaz',
                'status_ready': 'Listo para analizar',
                'status_done': '¡Análisis completado!',
                'status_fail': 'Error en el análisis.',
                'no_posts': 'No se encontraron publicaciones en el idioma seleccionado.',
                'comments': 'Comentarios',
                'sentiment': 'Sentimiento',
                'date': 'Fecha',
                'title': 'Título',
                'author': 'Autor',
                'score': 'Score',
                'positive': 'Positivo',
                'negative': 'Negativo',
                'neutral': 'Neutro',
                'sentimento': 'Sentimento',
                'graph_bar': 'Barras',
                'graph_score_sentiment': 'Score vs. Sentimiento',
                'graph_pie': 'Gráfico Circular'
            }
        }

    def update_interface_language(self):
        idioma = self.language_combo.currentText()
        t = self.get_translations()[idioma]
        self.polarization_label.setText(t['polarization'])
        self.config_group.setTitle(t['config_section'])
        self.subreddit_label.setText(t['subreddit'])
        self.sample_size_label.setText(t['sample_size'])
        self.analyze_btn.setText(t['analyze'])
        self.clear_btn.setText(t['clear'])
        self.export_btn.setText(t['export'])
        self.tabs.setTabText(0, t['statistics'])
        self.tabs.setTabText(1, t['data_table'])
        self.language_label.setText(t['language'])
        self.statusBar().showMessage(t['status_ready'])
        columns_to_show = ['id', 'title', 'author', 'score', 'created_utc', 'sentiment', 'sentimento']
        if self.data_table.columnCount() > 0:
            header_map = {
                'id': t.get('id', 'id'),
                'title': t.get('title', 'title'),
                'author': t.get('author', 'author'),
                'score': t.get('score', 'score'),
                'created_utc': t.get('created_utc', 'created_utc'),
                'sentiment': t.get('sentiment', 'sentiment'),
                'sentimento': t.get('sentimento', 'Sentimento')
            }
            headers = [header_map.get(col, col) for col in columns_to_show if col in self.current_data.columns]
            self.data_table.setHorizontalHeaderLabels(headers)
        
        current_graph_text = self.graph_type_combo.currentText()
        self.graph_type_combo.clear()
        self.graph_type_combo.addItems([t['graph_bar'], t['graph_score_sentiment'], t['graph_pie']])
        index = self.graph_type_combo.findText(current_graph_text)
        if index == -1:
            index = 0
        self.graph_type_combo.setCurrentIndex(index)

    def update_graph_section_visibility(self):
        if hasattr(self, 'graph_type_group'):
            visible = bool(self.subreddit_input.text().strip())
            self.graph_type_group.setVisible(visible)

    def __init__(self):
        super().__init__()
        self.processor = RedditDataProcessor()
        self.current_stats = None
        self.current_data = pd.DataFrame()
        
        self.graph_plot_widget = pg.PlotWidget()
        
        self.initUI()
        self.subreddit_input.setText("politics")
        self.start_analysis()

    def start_analysis(self):
        subreddit = self.subreddit_input.text().strip()
        sample_size = self.sample_size_spin.value()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        idioma = self.language_combo.currentText()
        lang_map = {"Português": "pt", "Inglês": "en", "Espanhol": "es"}
        lang_code = lang_map.get(idioma, "en")
        self.analysis_thread = AnalysisThread(self.processor, subreddit, sample_size)
        self.analysis_thread.progress_signal.connect(self.update_progress)
        self.analysis_thread.finished_signal.connect(lambda success, stats, data: self.analysis_finished_with_lang(success, stats, data, lang_code))
        self.analysis_thread.error_signal.connect(self.analysis_error)
        self.analysis_thread.start()

    def analysis_finished_with_lang(self, success, stats, data, lang_code):
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        if success:
            if 'lang' in data.columns:
                filtered_data = data[data['lang'] == lang_code]
                if filtered_data.empty:
                    QMessageBox.warning(self, "Aviso", "Nenhum post encontrado no idioma selecionado.")
                    self.current_stats = None
                    self.current_data = pd.DataFrame()
                    self.export_btn.setEnabled(False)
                    self.display_results()
                    return
                self.current_data = filtered_data
                self.current_stats = stats.copy()
                self.current_stats['total_posts'] = len(filtered_data)
                self.current_stats['avg_score'] = filtered_data['score'].mean()
                self.current_stats['avg_comments'] = filtered_data['num_comments'].mean()
                self.current_stats['avg_sentiment'] = filtered_data['sentiment_compound'].mean()
                self.current_stats['positive_posts'] = len(filtered_data[filtered_data['sentiment_compound'] > 0.05])
                self.current_stats['negative_posts'] = len(filtered_data[filtered_data['sentiment_compound'] < -0.05])
                self.current_stats['neutral_posts'] = len(filtered_data[(filtered_data['sentiment_compound'] >= -0.05) & (filtered_data['sentiment_compound'] <= 0.05)])
            else:
                self.current_stats = stats
                self.current_data = data
            self.export_btn.setEnabled(True)
            self.display_results()
            self.statusBar().showMessage('Análise concluída!')
        else:
            self.statusBar().showMessage('Falha na análise.')

    def update_progress(self, message, value):
        self.statusBar().showMessage(message)
        self.progress_bar.setValue(value)

    def analysis_finished(self, success, stats, data):
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        if success:
            self.current_stats = stats
            self.current_data = data
            self.export_btn.setEnabled(True)
            self.display_results()
            self.statusBar().showMessage('Análise concluída!')
        else:
            self.statusBar().showMessage('Falha na análise.')

    def analysis_error(self, message):
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.statusBar().showMessage(message)

    def initUI(self):
        self.setWindowTitle('NEXPOL - Analisador de Polarização do Reddit')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        logo_label = QLabel()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, 'logo.jpg')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            pixmap = pixmap.scaledToWidth(180, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            logo_label.setText('NEXPOL')
            logo_label.setFont(QFont('Arial', 24, QFont.Bold))
            logo_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(logo_label)

        top_info_layout = QHBoxLayout()
        self.polarization_label = QLabel()
        self.polarization_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.polarization_label.setFont(QFont('Arial', 14, QFont.Bold))
        self.polarization_label.setStyleSheet('color: #1976D2; margin-bottom: 10px;')
        top_info_layout.addWidget(self.polarization_label, alignment=Qt.AlignLeft)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        top_info_layout.addWidget(self.progress_bar, alignment=Qt.AlignRight)
        main_layout.addLayout(top_info_layout)

        self.config_group = QGroupBox("Configuração da Análise")
        input_layout = QFormLayout()
        subreddit_layout = QHBoxLayout()
        self.subreddit_label = QLabel("Subreddit:")
        self.subreddit_input = QLineEdit("politics")
        self.clear_btn = QPushButton("Limpar")
        self.clear_btn.setToolTip("Limpar campo subreddit")
        self.clear_btn.clicked.connect(self.clear_all)
        subreddit_layout.addWidget(self.subreddit_input)
        subreddit_layout.addWidget(self.clear_btn)
        input_layout.addRow(self.subreddit_label, subreddit_layout)
        self.sample_size_label = QLabel("Tamanho da Amostra:")
        self.sample_size_spin = QSpinBox()
        self.sample_size_spin.setRange(10, 500)
        self.sample_size_spin.setValue(50)
        input_layout.addRow(self.sample_size_label, self.sample_size_spin)
        self.language_label = QLabel("Idioma da Interface:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Português", "Inglês", "Espanhol"])
        self.language_combo.setCurrentIndex(0)
        self.language_combo.currentIndexChanged.connect(self.update_interface_language)
        input_layout.addRow(self.language_label, self.language_combo)

        self.graph_type_group = QGroupBox("Tipo de Gráfico")
        graph_type_layout = QHBoxLayout()
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Barras", "Score vs. Sentimento", "Setores (Pizza)"])
        self.graph_type_combo.setCurrentIndex(0)
        self.graph_type_combo.currentIndexChanged.connect(self.display_graph)
        graph_type_layout.addWidget(QLabel("Escolha o tipo de gráfico:"))
        graph_type_layout.addWidget(self.graph_type_combo)
        self.graph_type_group.setLayout(graph_type_layout)
        self.graph_type_group.setVisible(False)
        input_layout.addRow(self.graph_type_group)

        self.config_group.setLayout(input_layout)
        main_layout.addWidget(self.config_group)
        
        btn_layout = QHBoxLayout()
        self.analyze_btn = QPushButton("Iniciar Análise")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.export_btn = QPushButton("Exportar Dados")
        self.export_btn.clicked.connect(self.export_data)
        self.export_btn.setEnabled(False)
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addWidget(self.export_btn)
        main_layout.addLayout(btn_layout)

        self.tabs = QTabWidget()
        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        self.tabs.addTab(self.stats_widget, "Estatísticas")
        self.data_table = QTableWidget()
        self.tabs.addTab(self.data_table, "Dados")
        
        self.graph_widget = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_widget)
        self.graph_layout.addWidget(self.graph_plot_widget)
        self.tabs.addTab(self.graph_widget, "Gráfico")
        main_layout.addWidget(self.tabs)
        
        self.update_interface_language()
        self.subreddit_input.textChanged.connect(lambda: self.update_graph_section_visibility())
        self.update_graph_section_visibility()
    
    def clear_graph(self):
        self.graph_plot_widget.clear()

    def display_graph(self):
        if self.current_data.empty or self.current_stats is None:
            self.clear_graph()
            return

        self.graph_plot_widget.clear()
        
        self.graph_plot_widget.setMouseEnabled(x=True, y=True)
        self.graph_plot_widget.setMenuEnabled(True)
        self.graph_plot_widget.setClipToView(True)

        sentiment_counts = {
            'Positivo': self.current_stats.get('positive_posts', 0),
            'Neutro': self.current_stats.get('neutral_posts', 0),
            'Negativo': self.current_stats.get('negative_posts', 0)
        }
        
        labels = list(sentiment_counts.keys())
        values = list(sentiment_counts.values())
        
        graph_type = self.graph_type_combo.currentText()
        idioma = self.language_combo.currentText()
        t = self.get_translations()[idioma]

        # Ajuste o fundo para um cinza escuro mais suave para visualização
        self.graph_plot_widget.setBackground('#2a2a2a') 
        self.graph_plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.graph_plot_widget.getAxis('bottom').setPen('w')
        self.graph_plot_widget.getAxis('left').setPen('w')
        self.graph_plot_widget.getAxis('bottom').setTextPen('w')
        self.graph_plot_widget.getAxis('left').setTextPen('w')
        self.graph_plot_widget.getPlotItem().setTitle(f'Distribuição de Sentimentos - r/{self.current_stats["subreddit"]}', color='w')

        if graph_type == t['graph_bar']:
            self.graph_plot_widget.setLabel('bottom', 'Sentimento', color='w')
            self.graph_plot_widget.setLabel('left', 'Contagem de Posts', color='w')
            self.graph_plot_widget.setAspectLocked(False)
            
            colors = [(46, 204, 113), (241, 196, 15), (231, 76, 60)] 
            
            bg = pg.BarGraphItem(x=[1, 2, 3], height=values, width=0.6, brushes=colors)
            self.graph_plot_widget.addItem(bg)
            
            for i, val in enumerate(values):
                text_item = pg.TextItem(str(val), anchor=(0.5, 0), color='w')
                text_item.setPos(i + 1, val + (max(values) * 0.05)) 
                self.graph_plot_widget.addItem(text_item)
            
            ticks = [(1, t['positive']), (2, t['neutral']), (3, t['negative'])]
            ax = self.graph_plot_widget.getAxis('bottom')
            ax.setTicks([ticks])
        
        elif graph_type == t['graph_score_sentiment']:
            self.graph_plot_widget.setLabel('bottom', 'Score de Sentimento', color='w')
            self.graph_plot_widget.setLabel('left', 'Pontuação (Score)', color='w')
            self.graph_plot_widget.setAspectLocked(False)
            
            if 'sentiment_compound' in self.current_data.columns and 'score' in self.current_data.columns:
                scatter_plot = pg.ScatterPlotItem(
                    self.current_data['sentiment_compound'],
                    self.current_data['score'],
                    pen=pg.mkPen(None),
                    brush=pg.mkBrush(29, 110, 185, 200),
                    size=10
                )
                self.graph_plot_widget.addItem(scatter_plot)

            ax = self.graph_plot_widget.getAxis('bottom')
            ax.setTicks([
                [(0.8, t['positive'])],
                [(0, t['neutral'])],
                [(-0.8, t['negative'])]
            ])
            
        elif graph_type == t['graph_pie']:
            self.graph_plot_widget.showGrid(x=False, y=False)
            self.graph_plot_widget.setLabel('bottom', '')
            self.graph_plot_widget.setLabel('left', '')
            self.graph_plot_widget.hideAxis('bottom')
            self.graph_plot_widget.hideAxis('left')
            self.graph_plot_widget.setAspectLocked(True) 
            
            colors_pie = [(46, 204, 113), (241, 196, 15), (231, 76, 60)] 
            
            total = sum(values)
            if total == 0:
                return
            
            start_angle = 90
            
            for i, val in enumerate(values):
                end_angle = start_angle - (val / total * 360)
                
                wedge_path = pg.QtGui.QPainterPath()
                wedge_path.moveTo(0, 0)
                wedge_path.arcTo(-0.9, -0.9, 1.8, 1.8, start_angle, end_angle - start_angle)
                wedge_path.closeSubpath()
                
                brush = pg.mkBrush(colors_pie[i])
                item = pg.GraphicsObject()
                item.paint = lambda p, *args, path=wedge_path, brush=brush: p.fillPath(path, brush)
                item.boundingRect = lambda: pg.QtCore.QRectF(-1, -1, 2, 2)
                self.graph_plot_widget.addItem(item)
                
                angle_mid = (start_angle + end_angle) / 2
                radius_text = 1.1
                x_text = radius_text * math.cos(math.radians(angle_mid))
                y_text = radius_text * math.sin(math.radians(angle_mid))
                
                percentage = (val / total) * 100
                
                text_content = f"{labels[i]}\n{val} posts\n({percentage:.1f}%)"
                
                # Definir cor do texto para branco
                text_item = pg.TextItem(text_content, anchor=(0.5, 0.5), color='w')
                
                text_item.setPos(x_text, y_text)
                self.graph_plot_widget.addItem(text_item)
                
                start_angle = end_angle

    def export_data(self):
        if self.current_data.empty:
            QMessageBox.warning(self, "Erro", "Nenhum dado para exportar")
            return
        
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Dados", "reddit_analysis.csv", 
            "CSV Files (*.csv);;Excel Files (*.xlsx)", options=options
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.current_data.to_csv(file_path, index=False, encoding='utf-8')
                else:
                    self.current_data.to_excel(file_path, index=False)
                
                QMessageBox.information(self, "Sucesso", f"Dados exportados para: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao exportar dados: {str(e)}")

def main():
    app = QApplication(sys.argv)
    
    # Define a cor de fundo e a cor padrão para elementos visuais
    pg.setConfigOption('background', '#2a2a2a')
    pg.setConfigOption('foreground', 'w')
    
    app.setStyle('Fusion')

    auth = AuthWindow()
    auth.accepted = False
    if auth.exec_() == QDialog.Accepted or getattr(auth, 'accepted', False):
        window = RedditAnalyzerGUI()
        window.language_combo.setCurrentIndex(0) 
        window.subreddit_input.clear()
        window.sample_size_spin.setValue(10)
        window.update_graph_section_visibility()
        window.current_stats = None
        window.current_data = pd.DataFrame()
        window.polarization_label.setText("Polarização: N/A")
        window.data_table.setRowCount(0)
        window.clear_graph()
        window.export_btn.setEnabled(False)
        window.show()
        overlay = WelcomeOverlay(window)
        overlay.show()
        QTimer.singleShot(2000, overlay.close)
        sys.exit(app.exec_())
    else:
        sys.exit()

if __name__ == '__main__':
    main()
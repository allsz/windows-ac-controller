import sys
from PySide6 import QtCore, QtGui, QtWidgets

class FloatingTrayWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        # 1. Configurações de Janela Frameless e Translucida
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.Tool  # Não cria ícone na barra de tarefas principal
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Tamanho inicial do popup (340px de largura x 460px de altura)
        self.setFixedSize(360, 480)
        
        # 2. Layout e Container interno com cantos arredondados e sombra
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)  # Margem para sombra suave
        
        # Card principal (Container escuro)
        self.container = QtWidgets.QFrame(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            QFrame#MainContainer {
                background-color: #121316;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 24px;
            }
        """)
        
        # Efeito de sombra (Drop Shadow suave)
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QtGui.QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        self.container.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.container)
        
        # Conteúdo de teste dentro do container (para validação da Etapa 2)
        card_layout = QtWidgets.QVBoxLayout(self.container)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(14)
        
        # Cabeçalho
        header_layout = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("LG Dual Inverter")
        title_label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold; font-family: 'Segoe UI', sans-serif;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.status_badge = QtWidgets.QLabel(" Conectado ")
        self.status_badge.setStyleSheet("""
            color: #4ADE80;
            background-color: rgba(74, 222, 128, 0.15);
            font-size: 11px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 10px;
        """)
        header_layout.addWidget(self.status_badge)
        card_layout.addLayout(header_layout)
        
        # Separador sutil
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.08); max-height: 1px;")
        card_layout.addWidget(sep)
        
        # Informações da Etapa 2
        info_label = QtWidgets.QLabel(
            "<b>Etapa 2 - Validação de Janela & Tray</b><br><br>"
            "✓ Janela frameless flutuante<br>"
            "✓ Cantos arredondados (24px)<br>"
            "✓ Posicionamento dinâmico na bandeja<br>"
            "✓ Fecha automaticamente ao clicar fora (blur)<br><br>"
            "<i>(Na Etapa 3 vamos montar todo o visual idêntico ao seu mockup!)</i>"
        )
        info_label.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.5;")
        info_label.setWordWrap(True)
        card_layout.addWidget(info_label)
        
        card_layout.addStretch()
        
        # Botão de teste fechar
        btn_close = QtWidgets.QPushButton("Ocultar Janela")
        btn_close.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #27272A;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 10px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #3F3F46;
            }
        """)
        btn_close.clicked.connect(self.hide)
        card_layout.addWidget(btn_close)

    def reposition_above_tray(self):
        """Calcula as coordenadas perfeitas acima do ícone na bandeja do Windows"""
        screen = QtGui.QGuiApplication.primaryScreen()
        avail = screen.availableGeometry()  # Área útil (desconta a barra de tarefas)
        cursor_pos = QtGui.QCursor.pos()
        
        w = self.width()
        h = self.height()
        
        # X centralizado com o cursor do mouse onde o usuário clicou no tray
        x = cursor_pos.x() - (w // 2)
        
        # Evitar que a janela ultrapasse as bordas da tela
        margin = 12
        if x < avail.left() + margin:
            x = avail.left() + margin
        elif x + w > avail.right() - margin:
            x = avail.right() - margin - w
            
        # Y posicionado rente à área útil inferior (em cima da barra de tarefas)
        y = avail.bottom() - h - margin
        
        self.move(x, y)

    def show_popup(self):
        """Posiciona, exibe e ativa foco da janela"""
        self.reposition_above_tray()
        self.show()
        self.raise_()
        self.activateWindow()

    def changeEvent(self, event: QtCore.QEvent):
        """Detecta quando a janela perde o foco (clique fora do popup) para auto-ocultar"""
        if event.type() == QtCore.QEvent.Type.ActivationChange:
            if not self.isActiveWindow():
                # Pequeno timer para não conflitar com cliques repetidos no ícone
                QtCore.QTimer.singleShot(120, self._check_and_hide_on_blur)
        super().changeEvent(event)

    def _check_and_hide_on_blur(self):
        if not self.isActiveWindow():
            self.hide()


def create_tray_icon_pixmap() -> QtGui.QPixmap:
    """Gera um ícone elegante de Ar Condicionado em alta resolução programaticamente"""
    pixmap = QtGui.QPixmap(64, 64)
    pixmap.fill(QtCore.Qt.GlobalColor.transparent)
    
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    
    # Fundo do ícone (círculo escuro suave)
    painter.setBrush(QtGui.QBrush(QtGui.QColor(30, 32, 38)))
    painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 40), 2))
    painter.drawRoundedRect(4, 4, 56, 56, 16, 16)
    
    # Desenho estilizado do corpo do ar condicionado
    painter.setBrush(QtGui.QBrush(QtGui.QColor(240, 240, 245)))
    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.drawRoundedRect(12, 16, 40, 18, 4, 4)
    
    # Linha inferior da aleta do ar
    painter.setPen(QtGui.QPen(QtGui.QColor(180, 185, 195), 2))
    painter.drawLine(15, 30, 49, 30)
    
    # Feixes de ar azul fresco (Dual Inverter)
    pen_air = QtGui.QPen(QtGui.QColor(56, 189, 248), 2.5)
    pen_air.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_air)
    painter.drawLine(18, 38, 18, 46)
    painter.drawLine(28, 38, 28, 49)
    painter.drawLine(36, 38, 36, 49)
    painter.drawLine(46, 38, 46, 46)
    
    painter.end()
    return pixmap


class LGThinQTrayApp:
    def __init__(self):
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Mantém o app rodando no tray mesmo com janela fechada
        
        # Cria a janela flutuante
        self.window = FloatingTrayWindow()
        
        # Cria o ícone na bandeja do sistema (Tray)
        self.icon_pixmap = create_tray_icon_pixmap()
        self.tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(self.icon_pixmap), self.app)
        self.tray.setToolTip("LG Dual Inverter - Ar Condicionado")
        
        # Menu de contexto (botão direito no ícone)
        menu = QtWidgets.QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #18181B;
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI', sans-serif;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #27272A;
            }
        """)
        action_open = menu.addAction("Abrir Painel")
        action_open.triggered.connect(self.toggle_window)
        
        menu.addSeparator()
        
        action_quit = menu.addAction("Sair")
        action_quit.triggered.connect(self.quit_app)
        
        self.tray.setContextMenu(menu)
        
        # Clique com botão esquerdo no ícone da bandeja
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()
        
        print("Tray Icon inicializado com sucesso!")
        print("Clique com botao esquerdo no icone da bandeja (perto do relogio) para abrir a janela.")

    def on_tray_activated(self, reason):
        if reason in (QtWidgets.QSystemTrayIcon.ActivationReason.Trigger, QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick):
            self.toggle_window()

    def toggle_window(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show_popup()

    def quit_app(self):
        self.tray.hide()
        self.app.quit()

    def run(self):
        return self.app.exec()


if __name__ == "__main__":
    tray_app = LGThinQTrayApp()
    # Abre a janela uma vez no início para você já ver o resultado!
    QtCore.QTimer.singleShot(400, tray_app.window.show_popup)
    sys.exit(tray_app.run())

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QListWidget, QListWidgetItem, QLabel, QFrame)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont

from ui.upload_widget import UploadWidget  # 导入上传文件窗口类

class SidebarWidget(QWidget):
    """可折叠侧边栏"""
    # 定义信号
    paper_selected = pyqtSignal(str)  # 论文选择信号，传递论文ID
    upload_file = pyqtSignal(str)  # 上传文件信号，传递文件路径（转发）
    pause_processing = pyqtSignal()  # 暂停处理信号（转发）
    resume_processing = pyqtSignal()  # 继续处理信号（转发）
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.collapsed_width = 50
        self.expanded_width = 250  # 减小侧边栏宽度
        self.is_expanded = True
        self.setMaximumWidth(self.expanded_width)  # 设置最大宽度
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # 减少间距
        
        # 标题和折叠按钮
        header_frame = QFrame()
        header_frame.setObjectName("sidebarHeader")
        header_frame.setStyleSheet("""
            #sidebarHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #1a237e, stop:1 #0d47a1);
                color: white;
                border-bottom: 1px solid #0a1855;
            }
        """)
        header_frame.setFixedHeight(40)  # 固定高度与其他标题栏一致
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 0, 10, 0)
        
        title_font = QFont("Source Han Sans SC", 11, QFont.Weight.Bold)
        self.title_label = QLabel("论文列表")
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        
        # 固定位置的折叠按钮容器
        button_container = QWidget()
        button_container.setFixedWidth(30)
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.toggle_button = QPushButton("<<")
        self.toggle_button.setMaximumWidth(30)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                border: none;
                color: white;
                font-weight: bold;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 4px;
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        
        button_layout.addWidget(self.toggle_button)
        
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(button_container, 0, Qt.AlignmentFlag.AlignRight)
        
        # 论文列表容器
        list_container = QFrame()
        list_container.setObjectName("listContainer")
        list_container.setStyleSheet("""
            #listContainer {
                background-color: #f0f4f8;
            }
        """)
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # 论文列表
        self.paper_list = QListWidget()
        self.paper_list.setObjectName("paperList")
        self.paper_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.paper_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.paper_list.setStyleSheet("""
            #paperList {
                background-color: #f0f4f8;
                border: none;
                outline: none;
            }
            #paperList QScrollBar:vertical {
                width: 0px;
                background: transparent;
            }
            #paperList QScrollBar:horizontal {
                height: 0px;
                background: transparent;
            }
            #paperList QScrollBar::handle:vertical,
            #paperList QScrollBar::add-line:vertical,
            #paperList QScrollBar::sub-line:vertical,
            #paperList QScrollBar::add-page:vertical,
            #paperList QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #dbe2ef;
                color: #2c3e50;
                width: 100%;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                               stop:0 #1a237e, stop:1 #283593);
                color: white;
                border-radius: 6px;
                margin: 2px 5px;
            }
            QListWidget::item:hover:!selected {
                background-color: #e3f2fd;
                border-radius: 6px;
                margin: 2px 5px;
            }
        """)
        
        # 连接论文列表点击信号
        self.paper_list.itemClicked.connect(self.on_paper_item_clicked)
        
        list_layout.addWidget(self.paper_list)
        
        # 创建上传文件窗口
        self.upload_widget = UploadWidget()
        
        # 连接上传文件窗口的信号
        self.upload_widget.upload_file.connect(self.on_upload_file)
        self.upload_widget.pause_processing.connect(self.on_pause_processing)
        self.upload_widget.resume_processing.connect(self.on_resume_processing)
        
        # 添加到布局
        layout.addWidget(header_frame)
        layout.addWidget(list_container)
        layout.addWidget(self.upload_widget)
        
        self.setLayout(layout)
    
    def toggle_sidebar(self):
        """切换侧边栏展开/折叠状态"""
        self.is_expanded = not self.is_expanded
        
        target_width = self.expanded_width if self.is_expanded else self.collapsed_width
        
        # 创建动画
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(300)
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        # 同时设置最小宽度
        self.min_anim = QPropertyAnimation(self, b"minimumWidth")
        self.min_anim.setDuration(300)
        self.min_anim.setStartValue(self.width())
        self.min_anim.setEndValue(target_width)
        self.min_anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        
        # 更新按钮文本
        if self.is_expanded:
            button_text = "<<"
        else:
            button_text = ">>"
        
        self.toggle_button.setText(button_text)
        
        # 显示/隐藏其他内容
        self.title_label.setVisible(self.is_expanded)
        self.paper_list.setVisible(self.is_expanded)
        self.upload_widget.setVisible(self.is_expanded)
        
        # 如果正在折叠，且详情面板可见，先隐藏详情面板
        if not self.is_expanded:
            self.upload_widget.close_details_if_open()
        
        # 启动动画
        self.animation.start()
        self.min_anim.start()
    
    def load_papers(self, papers_index):
        """加载论文索引到列表"""
        self.paper_list.clear()
        for paper in papers_index:
            # 优先使用translated_title作为显示文本
            title = paper.get('translated_title', '') or paper.get('title', '') or paper.get('id', '')
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, paper)
            self.paper_list.addItem(item)
    
    def on_paper_item_clicked(self, item):
        """处理论文项点击事件，发出paper_selected信号"""
        paper = item.data(Qt.ItemDataRole.UserRole)
        if paper:
            # 发送论文选择信号
            self.paper_selected.emit(paper.get('id'))
            
    def on_upload_file(self, file_path):
        """处理上传文件事件，转发上传文件信号"""
        self.upload_file.emit(file_path)
        
    def on_pause_processing(self):
        """处理暂停处理事件，转发暂停处理信号"""
        self.pause_processing.emit()
        
    def on_resume_processing(self):
        """处理继续处理事件，转发继续处理信号"""
        self.resume_processing.emit()
        
    def update_upload_status(self, file_name, stage, progress, pending_count):
        """更新上传状态
        
        Args:
            file_name: 当前处理的文件名
            stage: 当前处理阶段
            progress: 处理进度值 (0-100)
            pending_count: 待处理文件数量
        """
        self.upload_widget.update_upload_status(file_name, stage, progress, pending_count)
# nuclei_gui.py
import os
import sys 
import subprocess 
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox, QComboBox, QListWidget, QListWidgetItem, QLabel
from PyQt6.QtCore import Qt 
from template_search import search_templates, write_results_to_file, read_template_content 

class TemplateSearchApp(QWidget): 
    def __init__(self): 
        super().__init__() 
        self.initUI() 

    def initUI(self):
        self.setWindowTitle('Template Search and Nuclei Scanner with PyQt6')
        self.setGeometry(100, 100, 800, 600)
 
        # 布局
        main_layout = QVBoxLayout()
 
        # 输入框和搜索按钮
        input_layout = QHBoxLayout()
 
        # 添加搜索路径输入框
        self.search_path = QLineEdit(self)
        self.search_path.setPlaceholderText("Enter search path for templates")
        self.search_path.setText("/home/user/nuclei-templates/")  # 设置nuclei模板默认路径
 
        self.search_term = QLineEdit(self)
        self.search_term.returnPressed.connect(self.search_templates)
 
        search_button = QPushButton('Search Templates', self)
        search_button.clicked.connect(self.search_templates)
 
        input_layout.addWidget(self.search_path)
        input_layout.addWidget(self.search_term)
        input_layout.addWidget(search_button)
 
        # Nuclei 部分输入框和按钮
        nuclei_layout_container = QWidget(self)
        nuclei_layout_container_layout = QVBoxLayout(nuclei_layout_container)  # 修改为QVBoxLayout以适应多行布局
 
        # Nuclei command 输入框及标签
        nuclei_command_label = QLabel("Nuclei Command Arguments:", self)
        nuclei_layout_container_layout.addWidget(nuclei_command_label)
        self.custom_command = QLineEdit(self)
        self.custom_command.setPlaceholderText("Enter custom nuclei command arguments")
        nuclei_layout_container_layout.addWidget(self.custom_command)
 
        # URL 下拉框、目标输入框和浏览按钮
        self.nuclei_branch = QComboBox(self)
        self.nuclei_branch.addItems(["URL", "URL File"])
        self.nuclei_branch.currentIndexChanged.connect(self.update_nuclei_inputs)
 
        self.nuclei_target = QLineEdit(self)
 
        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_nuclei_target)
 
        nuclei_sublayout = QHBoxLayout()
        nuclei_sublayout.addWidget(self.nuclei_branch)
        nuclei_sublayout.addWidget(self.nuclei_target)
        nuclei_sublayout.addWidget(self.browse_button)
 
        nuclei_layout_container_layout.addLayout(nuclei_sublayout)
 
        export_layout = QHBoxLayout()
        self.export_dir = QLineEdit(self)
        self.export_dir.setPlaceholderText("Enter export directory path")
        self.export_dir.setText("/home/user/Desktop/results/")  # nuclei结果输出路径
        export_layout.addWidget(QLabel("Nuclei Result Directory:", self))  # 添加标签以提高用户友好性
        export_layout.addWidget(self.export_dir)
 
        # 将之前的nuclei布局容器和新的导出目录布局添加到主布局中
        main_layout.addLayout(input_layout)
        main_layout.addLayout(export_layout)  # 添加导出目录布局
        main_layout.addWidget(nuclei_layout_container)
 
        # 模板选择列表
        self.template_list = QListWidget(self)
        self.template_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)  # 允许多选
 
        # 将全选按钮添加到主布局中，但放在模板选择列表之后
        self.select_all_button = QPushButton('Select All', self)
        self.select_all_button.clicked.connect(self.select_all_templates)
 
        # 多选按钮
        self.multi_select_button = QPushButton('Multi Select 10', self)
        self.multi_select_button.clicked.connect(self.multi_select_templates)
        self.current_multi_select_index = 0  # 用于记录当前多选的起始索引

        # 扫描按钮
        self.scan_button = QPushButton('Run Nuclei Scan', self)
        self.scan_button.clicked.connect(self.run_nuclei_scan)
        self.scan_button.setEnabled(False)

        # 实例化self.results_text
        self.results_text = QTextEdit(self)
        self.results_text.setReadOnly(True)
        self.results_text.hide()  # 隐藏它，但不从内存中删除

        # 添加到主布局（注意顺序）
        main_layout.addWidget(self.template_list)  # 添加模板选择列表
        main_layout.addWidget(self.select_all_button)  # 将全选按钮放在模板选择列表之后
        main_layout.addWidget(self.multi_select_button) # 将多选按钮添加到主布局中，放在全选按钮之后
        main_layout.addWidget(self.scan_button)

        self.setLayout(main_layout)
 
        # 初始化变量
        self.search_results = []
        self.selected_template_paths = []  # 存储选中的模板路径列表

        # 连接模板选择列表的itemChanged信号到select_templates方法（确保单选或全选后更新选中模板路径）
        self.template_list.itemChanged.connect(self.select_templates)

    def multi_select_templates(self):
        item_count = self.template_list.count()
        if item_count == 0:
            return
    
        if not hasattr(self, 'current_multi_select_index'):
            self.current_multi_select_index = 0  # 明确初始化为0，确保从第一项开始
    
        start_index = (self.current_multi_select_index) % item_count
        end_index = min(start_index + 10, item_count)
    
        for i in range(item_count):
            self.template_list.item(i).setCheckState(Qt.CheckState.Unchecked)
    
        for i in range(start_index, end_index):
            self.template_list.item(i).setCheckState(Qt.CheckState.Checked)
    
        # 更新为下一次的起始点（即这次选择的结束点的下一个索引，使用模运算实现循环）
        self.current_multi_select_index = end_index
        
    def update_nuclei_inputs(self): 
        # 根据选择的nuclei分支启用/禁用相应的输入框 
        if self.nuclei_branch.currentIndex() == 0: # URL 
            self.nuclei_target.setEnabled(True) 
            self.browse_button.setEnabled(False) 
        else: # URL File 
            self.nuclei_target.setEnabled(True) 
            self.browse_button.setEnabled(True) 

    def browse_nuclei_target(self): 
        # 浏览并选择URL文件 
        file_path, _ = QFileDialog.getOpenFileName(self, "Select URL File", "", "Text Files (*.txt);;All Files (*)") 
        if file_path: 
            self.nuclei_target.setText(file_path) 

    def search_templates(self): 
        search_term = self.search_term.text() 
        search_path = self.search_path.text() # 获取用户输入的搜索路径 
        self.search_results = search_templates(search_term, search_path) # 使用新的搜索路径，只返回文件路径列表 
        self.display_results(self.search_results)
        self.update_template_list()
        # 启用扫描按钮 
        self.scan_button.setEnabled(len(self.search_results) > 0) 

    def display_results(self, results): 
        result_texts = [f"{i + 1}. {result}\n" for i, result in enumerate(results)] 
        self.results_text.setPlainText("".join(result_texts)) 

    def update_template_list(self):
        self.template_list.clear()
        for result in self.search_results:
            item = QListWidgetItem(result)
            self.template_list.addItem(item)
            item.setCheckState(Qt.CheckState.Unchecked)

    def select_templates(self):
        # 重置多选按钮的索引值
        self.current_multi_select_index = 0
        
        # 获取选中的模板路径
        self.selected_template_paths = [self.search_results[i] for i in range(self.template_list.count())
                                       if self.template_list.item(i).checkState() == Qt.CheckState.Checked]

    def select_all_templates(self):
        # 选择或取消选择所有模板（这里实现为切换状态，即如果之前是未选中则全选，如果之前是全选则全不选）
        current_state = self.template_list.item(0).checkState() if self.template_list.count() > 0 else Qt.CheckState.Unchecked
        new_state = Qt.CheckState.Checked if current_state == Qt.CheckState.Unchecked else Qt.CheckState.Unchecked
        for i in range(self.template_list.count()):
            self.template_list.item(i).setCheckState(new_state)
        # 由于itemChanged信号会在每个项目状态改变时触发，因此不需要在这里手动调用self.select_templates()

    def run_nuclei_scan(self):
        # 获取用户输入的URL或URL文件路径 
        nuclei_target = self.nuclei_target.text() 
        if not nuclei_target: 
            QMessageBox.warning(self, "Warning", "Please enter a URL or select a URL file.") 
            return 

        # 获取用户自定义的指令 
        custom_command = self.custom_command.text() 

        # 获取用户自定义的导出目录路径
        export_path = self.export_dir.text()
        if not export_path or not os.path.isdir(export_path):
            QMessageBox.warning(self, "Warning", "Please enter a valid export directory path.")
            return

        # 检查是否有选中的模板路径 
        self.select_templates()
        if not self.selected_template_paths: 
            QMessageBox.warning(self, "Warning", "Please select at least one template.") 
            return 

        # 构建nuclei命令，使用选中的模板路径列表 
        nuclei_path = "nuclei/nuclei" # 需要替换为实际的nuclei路径 
        result_path = "/home/user/Desktop/results/" # nuclei结果输出路径
        template_paths_str = f'"{",".join(self.selected_template_paths)}"'
        if self.nuclei_branch.currentIndex() == 0: # URL 
            command = f'nuclei -u {nuclei_target} -t {template_paths_str} {custom_command} -o {export_path}nuclei_result.txt' 
            print(command)
        else: # URL File 
            command = f'nuclei -l {nuclei_target} -t {template_paths_str} {custom_command} -o {export_path}nuclei_result.txt' 
            print(command)

        # 执行命令（在新窗口中运行，以便不阻塞GUI） 
        subprocess.Popen(command, shell=True) 

        # 显示扫描开始的弹窗信息 
        #QMessageBox.information(self, "Scan Started", "Nuclei scan has been started.") 

    # 连接模板选择列表的itemChanged信号到select_templates方法（确保单选或全选后更新选中模板路径）
    def __post_init__(self):
        self.template_list.itemChanged.connect(self.select_templates)


if __name__ == '__main__': 
    app = QApplication(sys.argv) 
    ex = TemplateSearchApp() 
    ex.show() 
    sys.exit(app.exec())
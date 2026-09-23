#!/usr/bin/env python3
import os
import sys
from io import BytesIO

# Importaciones de PyQt6
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox, 
    QProgressBar, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

VERSION = '0.33 QT'
VERSDAT = '20/09/2026'
AUTOR = 'George Aghazarian - aghazarian@pm.me'

class PDFPagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Pager")
        self.setFixedSize(600, 380)

        # Variables de estado
        self.current_path = os.getcwd()

        self.setup_ui()
        self.refresh_pdf_list()

    def setup_ui(self):
        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # --- Selección de Carpeta ---
        folder_layout = QHBoxLayout()
        folder_label = QLabel("Carpeta:")
        self.entry_path = QLineEdit(self.current_path)
        self.entry_path.setReadOnly(True)
        self.btn_browse = QPushButton("Explorar...")
        self.btn_browse.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.entry_path)
        folder_layout.addWidget(self.btn_browse)
        main_layout.addLayout(folder_layout)

        # --- Selección de Archivo ---
        file_layout = QHBoxLayout()
        file_label = QLabel("Seleccione el PDF:")
        self.combo_files = QComboBox()
        self.btn_update = QPushButton("Actualizar")
        self.btn_update.clicked.connect(self.refresh_pdf_list)
        
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.combo_files)
        file_layout.addWidget(self.btn_update)
        main_layout.addLayout(file_layout)

        # --- Tamaño de Fuente ---
        font_layout = QHBoxLayout()
        font_label = QLabel("Tamaño de fuente:")
        self.spin_font = QSpinBox()
        self.spin_font.setRange(1, 100)
        self.spin_font.setValue(18)
        
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.spin_font)
        font_layout.addStretch() # Empuja el spinbox a la izquierda
        main_layout.addLayout(font_layout)

        # --- Página de Inicio ---
        page_layout = QHBoxLayout()
        page_label = QLabel("Numerar desde pág:")
        self.spin_start = QSpinBox()
        self.spin_start.setRange(1, 10000)
        self.spin_start.setValue(1)
        
        page_layout.addWidget(page_label)
        page_layout.addWidget(self.spin_start)
        page_layout.addStretch()
        main_layout.addLayout(page_layout)

        # --- Barra de Progreso ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        main_layout.addWidget(self.progress)

        # --- Botón Ejecutar ---
        self.btn_run = QPushButton("Generar PDF Numerado")
        self.btn_run.setFixedHeight(40)
        self.btn_run.clicked.connect(self.process_pdf)
        main_layout.addWidget(self.btn_run)

        # Footer
        footer_label = QLabel(f"{VERSION} - {VERSDAT} - {AUTOR}")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("font-size: 10px; color: gray;")
        main_layout.addWidget(footer_label)

    def browse_folder(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta", self.current_path)
        if folder_selected:
            self.current_path = folder_selected
            self.entry_path.setText(folder_selected)
            os.chdir(folder_selected)
            self.refresh_pdf_list()

    def refresh_pdf_list(self):
        self.combo_files.clear()
        try:
            files = [f for f in os.listdir(self.current_path) if f.lower().endswith('.pdf')]
            if not files:
                self.combo_files.addItem("No se encontraron PDFs")
            else:
                self.combo_files.addItems(sorted(files))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo leer la carpeta: {e}")

    def process_pdf(self):
        filename = self.combo_files.currentText()
        
        if not filename or filename == "No se encontraron PDFs":
            QMessageBox.warning(self, "Error", "Por favor, seleccione un archivo de la lista.")
            return

        input_pdf = os.path.join(self.current_path, filename)
        base, _ = os.path.splitext(input_pdf)
        output_pdf = f"{base}_paginado.pdf"

        try:
            self.btn_run.setEnabled(False)
            
            reader = PdfReader(input_pdf)
            writer = PdfWriter()
            total_pages = len(reader.pages)
            
            tam_fnt = self.spin_font.value()
            pag_inicio = self.spin_start.value()

            for i in range(total_pages):
                page = reader.pages[i]
                ancho = float(page.mediabox.width)
                alto = float(page.mediabox.height)

                if i >= pag_inicio - 1:
                    texto = str((i + 1) - (pag_inicio - 1))
                else:
                    texto = ''

                if texto:
                    packet = BytesIO()
                    c = canvas.Canvas(packet, pagesize=(ancho, alto))
                    x_centro = ancho / 2
                    y_posicion = 20 
                    c.setFont("Helvetica-Bold", tam_fnt)
                    c.setFillColorRGB(1, 1, 1)
                    
                    # Sombra para legibilidad
                    desplazamientos = [
                        (-1, -1), (-1, 0), (-1, 1),
                        (0, -1),           (0, 1),
                        (1, -1),  (1, 0),  (1, 1)
                    ]
                    for dx, dy in desplazamientos:
                        c.drawCentredString(x_centro + dx, y_posicion + dy, texto)
                    
                    c.setFillColorRGB(0, 0, 0)
                    c.drawCentredString(x_centro, y_posicion, texto)
                    c.save()
                    packet.seek(0)
                    overlay = PdfReader(packet)
                    page.merge_page(overlay.pages[0])

                writer.add_page(page)
                
                # Actualizar progreso
                perc = int(((i + 1) / total_pages) * 100)
                self.progress.setValue(perc)
                QApplication.processEvents() # Evita que la ventana se congele

            with open(output_pdf, "wb") as f:
                writer.write(f)

            QMessageBox.information(self, "Éxito", f"Archivo guardado como:\n{output_pdf}")
            self.refresh_pdf_list()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Crítico", f"Ocurrió un error: {str(e)}")
        finally:
            self.btn_run.setEnabled(True)
            self.progress.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFPagerGUI()
    window.show()
    sys.exit(app.exec())

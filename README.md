# PDF Pager

Aplicación de escritorio (PyQt6) que agrega numeración de páginas a archivos PDF, usando pypdf y reportlab para el overlay.

Creado por George Aghazarian — aghazarian@pm.me

## Descargar para Windows

El EXE se compila automáticamente con GitHub Actions en cada push:

* **Artefacto**: pestaña *Actions* → run más reciente → **PDF-Pager-Windows** (requiere iniciar sesión en GitHub, se guarda 7 días).
* **Releases**: al crear un tag (`git tag v1.0 && git push origin v1.0`), el EXE se publica en *Releases*, descargable sin iniciar sesión.

## Desarrollo

    pip install -r requirements.txt
    python pdfpagerQT.py

## Compilar el EXE localmente

    pyinstaller --onefile --noconsole pdfpagerQT.py

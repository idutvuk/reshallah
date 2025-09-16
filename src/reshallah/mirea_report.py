import tempfile
import shutil
import os
import typst
from PyPDF2 import PdfMerger


def compile_mirea_report(directory_path: str, custom_titlepage: str = None) -> str:
    """
    Компилирует MIREA отчет используя встроенный шаблон.
    
    Args:
        directory_path: Путь к директории с файлом content.typ
        custom_titlepage: Опциональный путь к PDF файлу для титульной страницы
        
    Returns:
        Путь к созданному PDF файлу
        
    Raises:
        FileNotFoundError: Если не найден content.typ или шаблон
        RuntimeError: Если произошла ошибка компиляции Typst
    """
    directory_path = os.path.abspath(directory_path)
    
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")
    
    # Check if content.typ exists in the directory
    content_typ_path = os.path.join(directory_path, "content.typ")
    if not os.path.exists(content_typ_path):
        raise FileNotFoundError(f"content.typ file not found at {content_typ_path}. Directory path: {directory_path}. This is required for MIREA reports.")
    
    # Get the path to the mirea_report_template folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, "assets", "mirea_report_template")
    
    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"MIREA report template not found at {template_dir}")
    
    directory_name = os.path.basename(os.path.normpath(directory_path))
    parent_dir = os.path.dirname(os.path.abspath(directory_path))
    output_pdf_path = os.path.join(parent_dir, f"{directory_name}.pdf")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # First copy the template files
        for item in os.listdir(template_dir):
            src = os.path.join(template_dir, item)
            dst = os.path.join(temp_dir, item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
        
        # Then copy the user's content.typ file (overwriting template's content.typ)
        shutil.copy2(content_typ_path, os.path.join(temp_dir, "content.typ"))
        
        # Copy any other files from user's directory (but not overwriting main template files)
        template_files = {"main.typ",  "mirea-logo.png"}
        for item in os.listdir(directory_path):
            if item not in template_files and item != "content.typ":  # Skip content.typ as it's already copied
                src = os.path.join(directory_path, item)
                dst = os.path.join(temp_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
        
        # Compile using main.typ
        typ_file_path = os.path.join(temp_dir, "main.typ")
        
        output = typst.compile(
            typ_file_path,
            format="pdf",
            ppi=144.0
        )

        # If a custom title page is provided, merge it before the compiled report
        if custom_titlepage and os.path.exists(custom_titlepage):
            compiled_pdf_temp_path = os.path.join(temp_dir, "compiled.pdf")
            with open(compiled_pdf_temp_path, "wb") as compiled_file:
                compiled_file.write(output)

            merger = PdfMerger()
            try:
                merger.append(custom_titlepage)
                merger.append(compiled_pdf_temp_path)
                with open(output_pdf_path, "wb") as merged_out:
                    merger.write(merged_out)
            finally:
                merger.close()
        else:
            with open(output_pdf_path, "wb") as output_file:
                output_file.write(output)
    
    return output_pdf_path
import tempfile
import shutil
import os
import typst
from PyPDF2 import PdfMerger


def compile_directory_to_pdf(directory_path: str, content_file: str = None, content_directory: str = None, custom_titlepage: str = None) -> str:
    """
    Компилирует Typst документы из директории в PDF.
    
    Args:
        directory_path: Путь к директории с .typ файлами
        content_file: Опциональный путь к файлу для копирования как content.typ
        content_directory: Опциональный путь к директории с контентом
        custom_titlepage: Опциональный путь к PDF файлу для титульной страницы
        
    Returns:
        Путь к созданному PDF файлу
        
    Raises:
        FileNotFoundError: Если директория не существует или не найден файл main.typ
        RuntimeError: Если произошла ошибка компиляции Typst
    """
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")
    
    try:
        typ_file = next(f for f in os.listdir(directory_path) if f.endswith("main.typ"))
    except StopIteration:
        raise FileNotFoundError(f"No main.typ file found in directory: {directory_path}")
    
    directory_name = os.path.basename(os.path.normpath(directory_path))
    parent_dir = os.path.dirname(os.path.abspath(directory_path))
    output_pdf_path = os.path.join(parent_dir, f"{directory_name}.pdf")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copytree(directory_path, temp_dir, dirs_exist_ok=True)
        
        # Если передан content_file, копируем его как content.typ
        if content_file and os.path.exists(content_file):
            shutil.copy2(content_file, os.path.join(temp_dir, "content.typ"))
        
        # Если передана content_directory, копируем все содержимое и создаем content.typ
        if content_directory and os.path.exists(content_directory):
            # Копируем все файлы из content_directory в temp_dir
            for item in os.listdir(content_directory):
                src = os.path.join(content_directory, item)
                dst = os.path.join(temp_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
            
            # Ищем content.typ в content_directory
            content_typ_path = os.path.join(content_directory, "content.typ")
            if os.path.exists(content_typ_path):
                shutil.copy2(content_typ_path, os.path.join(temp_dir, "content.typ"))
        
        typ_file_path = os.path.join(temp_dir, typ_file)
        
        output = typst.compile(
            typ_file_path,
            format="pdf",
            ppi=144.0
        )

        # Если передан custom_titlepage, объединяем PDF'ы через PdfMerger
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


def compile_simple_typst(directory: str, output: str = "output") -> str:
    """
    Простая компиляция Typst документа (используется в CLI).
    
    Args:
        directory: Путь к директории с .typ файлами
        output: Имя выходного файла (без расширения)
        
    Returns:
        Путь к созданному PDF файлу
        
    Raises:
        FileNotFoundError: Если директория не существует или не найден .typ файл
        RuntimeError: Если произошла ошибка компиляции Typst
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    
    outfile_name = f"{output}.pdf"

    with tempfile.TemporaryDirectory() as temp_dir, open(outfile_name, "wb") as output_file:
        shutil.copytree(directory, temp_dir, dirs_exist_ok=True)
        
        typ_file = None
        for f in os.listdir(temp_dir):
            if f.endswith(".typ"):
                typ_file = f
                break

        if not typ_file:
            raise FileNotFoundError(f"No .typ file found in directory: {directory}")

        typ_file_path = os.path.join(temp_dir, typ_file)
        output = typst.compile(
            typ_file_path,
            format="pdf",
            ppi=144.0
        )

        output_file.write(output)
        
    return outfile_name

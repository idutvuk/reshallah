import tempfile
import shutil
import os
import typst


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
    """
    # Normalize the directory path
    directory_path = os.path.abspath(directory_path)
    
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
        
        # Handle custom titlepage if provided
        if custom_titlepage and os.path.exists(custom_titlepage):
            # Copy PDF file to temp directory
            titlepage_filename = os.path.basename(custom_titlepage)
            titlepage_temp_path = os.path.join(temp_dir, titlepage_filename)
            shutil.copy2(custom_titlepage, titlepage_temp_path)
            
            # Read main.typ and add titlepage inclusion
            main_typ_path = os.path.join(temp_dir, "main.typ")
            with open(main_typ_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            # Add muchpdf import and titlepage inclusion at the beginning
            pdf_include = (
                          f'#import "@preview/muchpdf:0.1.0": muchpdf\n\n'
                f'#set page (margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm))\n'
                          f'#muchpdf(read("{titlepage_filename}", encoding: none))\n\n')
            
            main_content = pdf_include + main_content
            
            with open(main_typ_path, 'w', encoding='utf-8') as f:
                f.write(main_content)
        
        # Compile using main.typ
        typ_file_path = os.path.join(temp_dir, "main.typ")
        
        output = typst.compile(
            typ_file_path,
            format="pdf",
            ppi=144.0
        )
        
        with open(output_pdf_path, "wb") as output_file:
            output_file.write(output)
    
    return output_pdf_path
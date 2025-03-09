import os
import subprocess
import sys

def md_to_pdf_with_chrome(md_file):
    if not md_file.endswith(".md"):
        print("错误：输入文件必须是 Markdown (.md) 文件")
        return

    base_name = os.path.splitext(md_file)[0]
    html_file = f"{base_name}.html"
    pdf_file = f"{base_name}.pdf"

    # 1. 使用 grip 生成 HTML
    print("使用 grip 生成 HTML...")
    try:
        subprocess.run(["grip", md_file, "--export", html_file], check=True)
    except FileNotFoundError:
        print("错误：未找到 grip，请先安装它：pip install grip")
        return

    # 2. 使用 Chrome headless 模式转换 HTML 为 PDF
    print("使用 Google Chrome 生成 PDF...")
    try:
        subprocess.run([
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--headless",
            "--disable-gpu",
            "--print-to-pdf=" + pdf_file,
            "file://" + os.path.abspath(html_file)
        ], check=True)
        print(f"转换成功：{pdf_file}")
    except FileNotFoundError:
        print("错误：未找到 Google Chrome，请先安装它：brew install --cask google-chrome")
    finally:
        os.remove(html_file)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python md_to_pdf.py <input.md>")
    else:
        md_to_pdf_with_chrome(sys.argv[1])

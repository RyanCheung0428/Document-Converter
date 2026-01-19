import os
import sys
from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter
import win32com.client


def convert_xlsx_to_pdf_win32(xlsx_path, pdf_path):
    """
    使用 win32com 將 Excel 文件轉換為 PDF（適用於 Windows）
    """
    try:
        # 創建 Excel 應用程式實例
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        
        # 打開工作簿
        workbook = excel.Workbooks.Open(str(xlsx_path))
        
        # 導出為 PDF
        workbook.ExportAsFixedFormat(0, str(pdf_path))
        
        # 關閉工作簿
        workbook.Close(False)
        excel.Quit()
        
        return True
    except Exception as e:
        print(f"轉換失敗 {xlsx_path}: {str(e)}")
        return False


def convert_folder_xlsx_to_pdf(folder_path, output_folder=None):
    """
    將指定資料夾內的所有 xlsx 文件轉換為 PDF
    
    參數:
        folder_path: 包含 xlsx 文件的資料夾路徑
        output_folder: PDF 輸出資料夾（如果為 None，則與源文件同目錄）
    """
    folder_path = Path(folder_path)
    
    if not folder_path.exists():
        print(f"錯誤：資料夾不存在 - {folder_path}")
        return
    
    # 如果指定了輸出資料夾，則創建它
    if output_folder:
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
    
    # 查找所有 xlsx 文件
    xlsx_files = list(folder_path.glob("*.xlsx"))
    
    if not xlsx_files:
        print(f"在資料夾 {folder_path} 中未找到 xlsx 文件")
        return
    
    print(f"找到 {len(xlsx_files)} 個 xlsx 文件")
    print("-" * 50)
    
    success_count = 0
    fail_count = 0
    
    for xlsx_file in xlsx_files:
        # 跳過臨時文件（以 ~ 開頭）
        if xlsx_file.name.startswith('~'):
            continue
        
        # 確定輸出路徑
        if output_folder:
            pdf_file = output_folder / f"{xlsx_file.stem}.pdf"
        else:
            pdf_file = xlsx_file.with_suffix('.pdf')
        
        print(f"正在轉換: {xlsx_file.name}")
        
        # 轉換文件
        if convert_xlsx_to_pdf_win32(xlsx_file.absolute(), pdf_file.absolute()):
            print(f"✓ 成功: {pdf_file.name}")
            success_count += 1
        else:
            print(f"✗ 失敗: {xlsx_file.name}")
            fail_count += 1
        
        print()
    
    print("-" * 50)
    print(f"轉換完成！")
    print(f"成功: {success_count} 個文件")
    print(f"失敗: {fail_count} 個文件")


def main():
    print("=" * 50)
    print("Excel 轉 PDF 工具")
    print("=" * 50)
    print()
    
    # 獲取資料夾路徑
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        folder_path = input("請輸入包含 xlsx 文件的資料夾路徑: ").strip()
    
    # 獲取輸出資料夾（可選）
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    else:
        output_folder = input("請輸入 PDF 輸出資料夾路徑（留空則與源文件同目錄）: ").strip()
        if not output_folder:
            output_folder = None
    
    print()
    convert_folder_xlsx_to_pdf(folder_path, output_folder)


if __name__ == "__main__":
    main()

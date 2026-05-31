import pandas as pd

# Имя вашего исходного Excel-файла
excel_file = 'Датасет грузоперевозки.xlsx'

# Читаем все листы из Excel-файла сразу
# sheet_name=None загружает все вкладки в виде словаря {Имя_листа: DataFrame}
all_sheets = pd.read_excel(excel_file, sheet_name=None)

# Проходим циклом по всем листам и сохраняем каждый в отдельный CSV
for sheet_name, df in all_sheets.items():
    # Формируем имя для нового CSV-файла
    csv_file_name = f"{excel_file.replace('.xlsx', '')} - {sheet_name}.csv"
    
    # Сохраняем в CSV. 
    # encoding='utf-8-sig' нужен, чтобы Excel потом корректно читал русские буквы
    df.to_csv(csv_file_name, index=False, encoding='utf-8-sig')
    print(f"Лист '{sheet_name}' успешно сохранен как: {csv_file_name}")
import data

if __name__ == "__main__":
    data = data.Data(data.Data.XLSX_PATH)
    data.load_from_raw()
    data.export_data()

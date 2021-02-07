import xlsxwriter

workbook = xlsxwriter.Workbook('tables.xlsx')
worksheet8 = workbook.add_worksheet()

data = [
    ['Apples', 10000, 5000, 8000, 6000],
    ['Pears', 2000, 3000, 4000, 5000],
    ['Bananas', 6000, 6000, 6500, 6000],
    ['Oranges', 500, 300, 200, 700],
]

caption = 'Table with user defined column headers'

# Set the columns widths.
worksheet8.set_column('B:G', 12)

# Write the caption.
worksheet8.write('B1', caption)

# Formula to use in the table.
formula = '=SUM(Table1[@[Quarter 1]:[Quarter 4]])'

# Add a table to the worksheet.
worksheet8.add_table('B3:G7', {'data': data,
                               'columns': [{'header': 'Product'},
                                           {'header': 'Quarter 1'},
                                           {'header': 'Quarter 2'},
                                           {'header': 'Quarter 3'},
                                           {'header': 'Quarter 4'},
                                           {'header': 'Year',
                                            'formula': formula},
                                           ]})

workbook.close()
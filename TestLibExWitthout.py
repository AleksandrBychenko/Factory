import formulas
import numpy as np
#from formulas import Parser, Array

a = np.array([[1,2,'= IF(A1>A2,"GREATER","LOWER")']])

#компилация формулы
func = formulas.Parser().ast(a[0][2])[1].compile()

#какик клетки использовали
use_cell = list(func.inputs)

print(list(func.inputs))

#из  клетки получаем номер строки и столбца и создаем масиив нужных данных
from openpyxl.utils import column_index_from_string
for i in range(len(use_cell)):
    cell_name =use_cell[i]
    column_name = cell_name[0] # Получаем букву столбца из имени ячейки
    row_number = int(cell_name[1:]) - 1  # Получаем номер строки из имени ячейки
    column_number = column_index_from_string(column_name) - 1  # Получаем номер столбца из буквы
    #data = data.append(a[column_number][row_number])
    use_cell[i] = a[column_number][row_number]
    print(use_cell[i])

# передаем массив нужных данных в функцию 
test = func(*use_cell)
print(test)


'''
#разбираем номер ячеки на номер столбца и ячейки 
from openpyxl.utils import column_index_from_string
#from formulas import parse_formula
#from formulas.parser import eval_formula

#достаем массив ячеек в формуле 
formula = a[0][2]
#cell = formulas.Cell('= IF(A1 > A2,"GREATER","LOWER")')
cells = formulas.Parser().ast(formula)[1].

# Создаем объект Parser
parser = formulas.

# Создаем объект Cell для ячейки, содержащей формулу
cell = formulas.Cell('A1')

# Получаем список ячеек, используемых в формуле
cell_list = parser.ast(cell.formula).get_cells()

# Выводим список ячеек
print(cell_list)




#данные нужных ячеек 
data = np.array([])

for i  in (len(cells)):
    cell_name = cells[i]
    column_name = cell_name[0]  # Получаем букву столбца из имени ячейки
    row_number = int(cell_name[1:] - 1)  # Получаем номер строки из имени ячейки
    column_number = column_index_from_string(column_name) - 1  # Получаем номер столбца из буквы
    data = data.append(a[column_number][row_number])

#result = eval_formula(formula, data)
result = eval_formula(formula, data)
print(result) 


#test = func(1,2)
#print(test)
'''


'''
# добовляем свою функцию 
FUNCTIONS = formulas.get_functions()
FUNCTIONS['MYFUNC'] = lambda x, y: 1 + y + x
func = formulas.Parser().ast('=MYFUNC(A1, A2)')[1].compile()
print(func(1, 2))

'''

'''
#узнаем ввиде массива каие столбцы в формуле 
from formulas import parse_formula

formula = '=SUM(B1:B5)'
cells = parse_formula(formula)
print(cells)
#Этот код выведет список ячеек, используемых в формуле: ['B1', 'B2', 'B3', 'B4', 'B5'].
'''

'''
#узнаем номер строки и столбца 
from openpyxl.utils import column_index_from_string

column_name = 'C'
column_number = column_index_from_string(column_name)
print(column_number) # Выведет 3


from openpyxl.utils import get_column_letter

column_number = 3
column_name = get_column_letter(column_number)
print(column_name) # Выведет 'C'
'''

'''
#узнаем номер  страки и столбца по ячейке 
from openpyxl.utils import column_index_from_string

cell_name = 'B3'
column_name = cell_name[0]  # Получаем букву столбца из имени ячейки
row_number = int(cell_name[1:])  # Получаем номер строки из имени ячейки
column_number = column_index_from_string(column_name)  # Получаем номер столбца из буквы

print(f'Столбец: {column_number}, Строка: {row_number}')

'''

'''
# отправляем вместо просто данных что-то другое ф функцию 

from formulas import eval_formula

data = {
    'A1': 1, 'A2': 2, 'A3': 3, 'A4': 4, 'A5': 5,
    'B1': 6, 'B2': 7, 'B3': 8, 'B4': 9, 'B5': 10
}

formula = '=SUM(A1:B5)'
result = eval_formula(formula, data)
print(result) # Выведет 55

# ----
from formulas import eval_formula

data = {
    'A1': 1, 'A2': 2, 'A3': 3, 'A4': 4, 'A5': 5,
    'B1': 6, 'B2': 7, 'B3': 8, 'B4': 9, 'B5': 10
}

formula = '=SUM(A1:B5)'
result = eval_formula(formula, data)
print(result) # Выведет 55

from formulas import eval_formula

data = [
    [1, 6],
    [2, 7],
    [3, 8],
    [4, 9],
    [5, 10]
]

formula = '=SUM(A1:B5)'
result = eval_formula(formula, data)
print(result) # Выведет 55

#-------
from formulas import eval_formula
import numpy as np

data = [1, 6, 2, 7, 3, 8, 4, 9, 5, 10]
data_2d = np.array(data).reshape(5, 2)

formula = '=SUM(A1:B5)'
result = eval_formula(formula, data_2d.tolist())
print(result) # Выведет 55

# -- 



'''

a = 0



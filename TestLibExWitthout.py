import formulas
func = formulas.Parser().ast('= IF(A1>A2,"GREATER","LOWER")')[1].compile()
print(list(func.inputs))
test = func(1,2)
print(test)
a = 0
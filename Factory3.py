from enum import Enum
from queue import PriorityQueue
from typing import Set
import random
from abc import abstractmethod

#from .Factory3 import Flowsheet

import numpy as np


def Compare(val1, val2):
    '''
    Method to compare float point values inside predefined accuracy interval
    Is used by NumericalProperty Calculate method
    '''
    return abs(val1 - val2) < 1e-5 +  + 1e-5 * (abs(val1) + abs(val2)) * 0.5

class UnitTypeEnum(Enum):
    '''
    Enumeration class including types of different physical values
    '''
    ACCELERATION = 1
    DELTA_P = 2
    DELTA_T = 3
    MOLAR_DENS = 4
    FRACTION = 5
    MASS_FRACTION = 6
    MOLAR_FRACTION = 7
    HEAT_FLOW = 8
    LENGTH = 9
    MASS = 10
    MASS_DENS = 11
    MASS_FLOW = 12
    MOLAR_ENTHALPY = 13
    MOLAR_ENTROPY = 14
    MOLAR_FLOW = 15
    PRESSURE = 16
    TEMPERATURE = 17
    UNITLESS = 18
    NONE = 19
    INDEX = 20
class PropertyStateEnum(Enum):
    '''
    Enumeration class including states of properties
    '''
    CALCULATED = 1
    SPECIFIED = 2
    DEFAULT = 3
class SolverStateEnum(Enum):
    '''
    Enumeration class including states of solver
    In Frozen state solver calls only forgetting pass for unitops, 
    in Active state solver also calls solving pass for unitops (see SequentialSolver.Solve()) 
    '''
    Frozen = 0,
    Active = 1


class UnitToSiConversion:
    '''
    Simple class fo values form si/to si conversions using known bias and factor
    '''
    def __init__(self, name, factor, bias):
        self._name = name
        self._factor = factor
        self._bias = bias

    def convert_to_si(self, value_not_si):
        return value_not_si * self._factor + self._bias

    def convert_from_si(self, value_in_si):
        return (value_in_si - self._bias) / self._factor
    
class Units:
    @staticmethod
    def ConvertValue(val, oldUnits: UnitToSiConversion, newUnits: UnitToSiConversion):
        return newUnits.convert_from_si(oldUnits.convert_to_si(val))
 
    UnitsLibrary: dict[UnitTypeEnum, dict[str, UnitToSiConversion]] = {
        UnitTypeEnum.ACCELERATION: {
            "m/s2": UnitToSiConversion("m/s2", 1.0, 0.0),
            "cm/s2": UnitToSiConversion("cm/s2", 0.01, 0.0),
            "ft/s2": UnitToSiConversion("ft/s2", 0.3048, 0.0)
        },
        UnitTypeEnum.DELTA_P: {
            "Pa": UnitToSiConversion("Pa", 1.0, 0.0),
            "atm": UnitToSiConversion("atm", 101325.0, 0.0),
            "kPa": UnitToSiConversion("kPa", 1e3, 0.0),
            "bar": UnitToSiConversion("bar", 1e5, 0.0),
            "MPa": UnitToSiConversion("MPa", 1e6, 0.0),
            "psi": UnitToSiConversion("psi", 6894.74482, 0.0),
        },
        UnitTypeEnum.DELTA_T: {
            "K": UnitToSiConversion("K", 1.0, 0.0),
            "C": UnitToSiConversion("C", 1.0, 0),
        },
        UnitTypeEnum.MOLAR_DENS: {
            "mole/m3": UnitToSiConversion("mole/m3", 1.0, 0.0),
            "kmole/m3": UnitToSiConversion("kmole/m3", 1e3, 0.0),
            "mole/l": UnitToSiConversion("mole/l", 1e3, 0.0),
            "mole/cm3": UnitToSiConversion("mole/cm3", 1e6, 0.0),
            "mole/ml": UnitToSiConversion("mole/ml", 1e6, 0.0),
            "lbmole/ft3": UnitToSiConversion("lbmole/ft3", 16.0185, 0.0),
        },
        UnitTypeEnum.FRACTION: {
            "": UnitToSiConversion("", 1.0, 0.0),
        },
        UnitTypeEnum.MASS_FRACTION: {
            "": UnitToSiConversion("", 1.0, 0.0),
        },
        UnitTypeEnum.MOLAR_FRACTION: {
            "": UnitToSiConversion("", 1.0, 0.0),
        },
        UnitTypeEnum.HEAT_FLOW: {
            "W": UnitToSiConversion("W", 1.0, 0.0),
            "J/s": UnitToSiConversion("J/s", 1.0, 0.0),
            "kW": UnitToSiConversion("kW", 1e3, 0.0),
            "MW": UnitToSiConversion("MW", 1e6, 0.0),
            "hp": UnitToSiConversion("hp", 745.69987158, 0.0),
            "kJ/s": UnitToSiConversion("kJ/s", 1e3, 0.0),
            "J/h": UnitToSiConversion("J/h", 0.0002777778, 0.0),
            "J/min": UnitToSiConversion("J/min", 0.0166666667, 0.0),
            "kJ/h": UnitToSiConversion("kJ/h", 0.2777777778, 0.0)
        },
        UnitTypeEnum.LENGTH: {
            "m": UnitToSiConversion("m", 1.0, 0.0),
            "km": UnitToSiConversion("km", 1e3, 0.0),
            "cm": UnitToSiConversion("cm", 1e-2, 0.0),
            "dm": UnitToSiConversion("dm", 1e-1, 0.0),
            "ft": UnitToSiConversion("ft", 0.3048, 0.0),
            "mm": UnitToSiConversion("mm", 1e-3, 0.0),
            "µm": UnitToSiConversion("µm", 1e-6, 0.0),
            "nm": UnitToSiConversion("nm", 1e-9, 0.0),
            "in": UnitToSiConversion("in", 0.0254, 0.0),
            "mi": UnitToSiConversion("mi", 1609.34, 0.0),
            "yd": UnitToSiConversion("yd", 0.9144, 0.0)
        },
        UnitTypeEnum.MASS: {
            "kg": UnitToSiConversion("kg", 1.0, 0.0),
            "g": UnitToSiConversion("g", 1e-3, 0.0),
            "mg": UnitToSiConversion("mg", 1e-6, 0.0),
            "tonn": UnitToSiConversion("tonn", 1e3, 0.0),
            "µg": UnitToSiConversion("µg", 1e-9, 0.0),
            "lbs": UnitToSiConversion("lbs", 0.45359237, 0.0),
            "oz": UnitToSiConversion("oz", 0.0283495231, 0.0)
        },
        UnitTypeEnum.MASS_DENS: {
            "kg/m3": UnitToSiConversion("kg/m3", 1.0, 0.0),
            "g/cm3": UnitToSiConversion("g/cm3", 1e3, 0.0),
            "g/m3": UnitToSiConversion("g/m3", 1e-3, 0.0),
            "kg/cm3": UnitToSiConversion("kg/cm3", 1e6, 0.0),
            "g/l": UnitToSiConversion("g/l", 1.0, 0.0),
            "t/m3": UnitToSiConversion("t/m3", 1e3, 0.0),
            "mg/cm3": UnitToSiConversion("mg/cm3", 1.0, 0.0),
            "lb/ft3": UnitToSiConversion("lb/ft3", 16.01845, 0.0),
            "lb/in3": UnitToSiConversion("lb/in3", 27680, 0.0)
        },
        UnitTypeEnum.MASS_FLOW: {
            "kg/s": UnitToSiConversion("kg/s", 1.0, 0.0),
            "kg/min": UnitToSiConversion("kg/min", 1.666667e-2, 0.0),
            "kg/h": UnitToSiConversion("kg/h", 2.777778e-4, 0.0),
            "t/h": UnitToSiConversion("t/h", 0.277778, 0.0),
            "g/s": UnitToSiConversion("g/s", 1e-3, 0.0),
            "g/h": UnitToSiConversion("g/h", 2.7778e-7, 0.0),
            "g/min": UnitToSiConversion("g/min", 1.6667e-5, 0.0)
        },
        UnitTypeEnum.MOLAR_ENTHALPY: {
            "J/mole": UnitToSiConversion("J/mole", 1.0, 0.0),
            "kJ/mole": UnitToSiConversion("kJ/mole", 1e3, 0.0),
            "J/kmole": UnitToSiConversion("J/kmole", 1e-3, 0.0)
        },
        UnitTypeEnum.MOLAR_ENTROPY: {
            "J/[mole*K]": UnitToSiConversion("J/[mole*K]", 1.0, 0.0),
            "kJ/[mole*K]": UnitToSiConversion("kJ/[mole*K]", 1e3, 0.0),
            "J/[kmole*K]": UnitToSiConversion("J/[kmole*K]", 1e-3, 0.0)
        },
        UnitTypeEnum.MOLAR_FLOW: {
            "mole/s": UnitToSiConversion("mole/s", 1.0, 0.0),
            "kmole/s": UnitToSiConversion("kmole/s", 1e3, 0.0),
            "mole/min": UnitToSiConversion("mole/min", 1.666667e-2, 0.0),
            "kmole/min": UnitToSiConversion("kmole/min", 16.66667, 0.0),
            "mole/h": UnitToSiConversion("mole/h", 2.777778e-4, 0.0),
            "kmole/h": UnitToSiConversion("kmole/h", 0.277778, 0.0)
        },
        UnitTypeEnum.PRESSURE: {
            "Pa": UnitToSiConversion("Pa", 1.0, 0.0),
            "atm": UnitToSiConversion("atm", 101325.0, 0.0),
            "kPa": UnitToSiConversion("kPa", 1e3, 0.0),
            "bar": UnitToSiConversion("bar", 1e5, 0.0),
            "MPa": UnitToSiConversion("MPa", 1e6, 0.0),
            "psi": UnitToSiConversion("psi", 6894.74482, 0.0),
            "kPag": UnitToSiConversion("kPag", 1e3, 101325.0),
            "MPag": UnitToSiConversion("MPag", 1e6, 101325.0)
        },
        UnitTypeEnum.TEMPERATURE: {
            "K": UnitToSiConversion("K", 1.0, 0.0),
            "C": UnitToSiConversion("C", 1, 273.15)
        },
        UnitTypeEnum.UNITLESS: {
            "": UnitToSiConversion("", 1.0, 0.0)
        },
        UnitTypeEnum.NONE: {
            "": UnitToSiConversion("", 1.0, 0.0)
        }
    }

# Forward declaration (To be seen by all classes)
class BaseUnitOp:
    pass
class SequentialSolver:
    pass


class NumericalProperty:
    '''
    Class incapsulating physical value - float point number of defined UnitType.
    '''

    @property
    def HasValue(self):
        '''
        Determines if value is present or none
        '''
        return not self.Value == None
    
    @property
    def Value(self):
        return self._value
    
    @property
    def PropertyState(self):
        return self._property_state
    
    @property
    def CalcBy(self):
        '''
        Object, who called Calculate() method for current property
        '''
        return self._calc_by

    @PropertyState.setter
    def PropertyState(self, state):
        self._property_state = state
        self.CanModify = self._property_state != PropertyStateEnum.CALCULATED

    @Value.setter
    def Value(self, value):
        if not self.CanModify:
            raise Exception(f"NumericalProperty error! Trying to set calculated property {self.Tag} of object {self.Owner.Name}!")
        self._value = value
        self.PropertyState = PropertyStateEnum.SPECIFIED
        self.TryTriggerSolve()

    @CalcBy.setter
    def CalcBy(self, objCalcBy : BaseUnitOp):
        self._calc_by = objCalcBy
        if self.TriggerSolve and self._calc_by is not None:
            objCalcBy.CalculatedTriggeringProperties[f"{self.Owner.Id}.{self.Tag}"]  = self

    def __init__(self, tag, unitType: UnitTypeEnum, owner : BaseUnitOp = None, triggerSolve = False, calcByObject : BaseUnitOp = None, defaultValue = None):
        self.Tag = tag
        self.UnitType = unitType
        self.TriggerSolve = triggerSolve
        self.Owner = owner
        self.PropertyState = PropertyStateEnum.CALCULATED if calcByObject is not None else (PropertyStateEnum.DEFAULT if defaultValue is not None else PropertyStateEnum.SPECIFIED)
        self.CalcBy = calcByObject
        self.Value = defaultValue
        self.NewValue = None


    def TryTriggerSolve(self):
        if self.TriggerSolve:
            self.Owner.TryAddToCalcQueue(True)
            self.Owner.TriggerSolver()

    def AddOwnerToSolver(self):
        self.Owner.TryAddToCalcQueue(False)

    def Calculate(self, calcvalue, ObjCalculator : BaseUnitOp = None):
        noChangesCalcs = False

        if not calcvalue is None and not self._value is None:
            if not Compare(calcvalue, self._value):
                raise Exception(f"NumericalProperty Calculate method error! Trying to calculate already calculated property \"{self.Tag}\" of object \"{self.Owner.Name}\"!")
            noChangesCalcs = True

        if not noChangesCalcs:
            self.NewValue = calcvalue
            if not self.Owner.VariableChanging(self):
                return
            self.PropertyState = PropertyStateEnum.CALCULATED
            self._value = self.NewValue
            self.CalcBy = ObjCalculator
            self.Owner.VariableChanged(self)
            if self.TriggerSolve and self.CalcBy is not self.Owner:
                self.AddOwnerToSolver()

    def Clear(self):
        self.PropertyState = PropertyStateEnum.SPECIFIED
        self._value = None
        self.CalcBy = None

    def SetValue(self, val, units=""):
        if not self.CanModify:
            raise Exception(f"NumericalProperty SetValue error! Property can't be modified: {self.Owner.Name}.{self.Tag}!")

        if units != "" and not units in Units.UnitsLibrary[self.UnitType].keys():
                raise Exception(f"NumericalProperty SetValue error! Units with name {units} are unavailable for type {self.UnitType}")
        
        self.NewValue = val if (val is None or units == "") else Units.UnitsLibrary[self.UnitType][units].convert_to_si(val)
        if not self.Owner.VariableChanging(self):
            return
        self.PropertyState = PropertyStateEnum.SPECIFIED
        self._value = self.NewValue
        self.Owner.VariableChanged(self)
        
        self.TryTriggerSolve()
       


    def GetValue(self, units=""):
        if units != "" and not units in Units.UnitsLibrary[self.UnitType]:
            raise Exception(f"NumericalProperty GetValue error!  Units with name {units} are unavailable for type {self.UnitType}")
        return self.Value if (self.Value is None or units == "") else Units.UnitsLibrary[self.UnitType][units].convert_from_si(self.Value) 

class Flowsheet:
    GlobalIdCounter = 0

    def __init__(self):
        self.StaticsSolver = SequentialSolver(self)
        self.ItemsDict: dict[int,BaseUnitOp] = {}

    def AddUnitOp(self, unitOp: BaseUnitOp):
        if unitOp.Name in self.ItemsDict.keys():
            raise Exception(f"Flowsheet error! UnitOp with name {unitOp.Name} already exists!")
        self.GlobalIdCounter += 1
        self.ItemsDict[unitOp.Name] = unitOp
        return self.GlobalIdCounter
    
    def ActivateSolver(self):
        self.StaticsSolver.SolverState = SolverStateEnum.Active
        self.Solve()

    def DisableSolver(self):
        self.StaticsSolver.SolverState = SolverStateEnum.Frozen

    def Solve(self):
        self.StaticsSolver.Solve()

class SequentialSolver:

    def __init__(self, ownerCase: Flowsheet):
        self.Owner = ownerCase
        self.SolverState = SolverStateEnum.Frozen
        self.ForgettingQueue : PriorityQueue[(int,BaseUnitOp)] = PriorityQueue()
        self.SolvingQueue : PriorityQueue[(int,BaseUnitOp)] = PriorityQueue()
        self.ForgettingIdSet: Set[int] = set()
        self.SolvingIdSet: Set[int] = set()
        self.IsSolving = False
        self.IsCurrentlySolvePass = False

    def TryAddObjectToForgettingQueue(self, ObjectToAdd : BaseUnitOp):
        if ObjectToAdd.Id not in self.ForgettingIdSet:
            self.ForgettingIdSet.add(ObjectToAdd.Id)
            self.ForgettingQueue.put((ObjectToAdd.CalcOrder, ObjectToAdd.Id, ObjectToAdd))
            return True
        return False

    def TryAddObjectToSolvingQueue(self, ObjectToAdd : BaseUnitOp):
        if ObjectToAdd.Id not in self.SolvingIdSet:
            self.SolvingIdSet.add(ObjectToAdd.Id)
            self.SolvingQueue.put((ObjectToAdd.CalcOrder,ObjectToAdd.Id, ObjectToAdd))
            return True
        return False

    def TryDequeueForgetting(self):
        if not self.ForgettingQueue.empty():
            order, id, element = self.ForgettingQueue.get()
            self.ForgettingIdSet.remove(id)
            return element
        return None

    def TryDequeueCalc(self):
        if not self.SolvingQueue.empty():
            order, id, element = self.SolvingQueue.get()
            self.SolvingIdSet.remove(id)
            return element
        return None
    
    def Solve(self):

        if self.IsSolving:
            raise Exception(f"Solver error! Solver already solving.")
    
        self.IsSolving = True

        print("")
        print("Forgetting PASS")
        
        while True:
            # Get Element from forgetting Queue collection
            elementF = self.TryDequeueForgetting()

            if not elementF is None:
                if self.IsCurrentlySolvePass:
                    print("")
                    print("Forgetting PASS")
                
                self.IsCurrentlySolvePass = False
                
                print(elementF.Name)
                
                # Clear All calculated properties
                elementF.ClearCalculatedProperties()
                
                # Call forgetting calculation of object
                elementF.Calculate(True)
                
                # Add object to Solving queue
                self.TryAddObjectToSolvingQueue(elementF)
                
                continue
            
            if self.SolverState is SolverStateEnum.Active:
                elementS = self.TryDequeueCalc()
                if not elementS is None:

                    if not self.IsCurrentlySolvePass:
                        print("")
                        print("Solving PASS")
                    
                    self.IsCurrentlySolvePass = True
                    
                    if elementS.IsCalculated:
                        continue
                    
                    print(elementS.Name)
                    
                    # Calculate object
                    elementS.Calculate(False)

                    continue

            # Finish loop if we reached this point
            break

        self.IsCurrentlySolvePass = False
        self.IsSolving = False

class BaseUnitOp:
    def __init__(self, name, Flwsht: Flowsheet, calcOrder = 500):
        self.Name = name
        self.Id = Flwsht.AddUnitOp(self)
        self.Owner = Flwsht

        self.CalcOrder = calcOrder


        self.IsCalculated = False
        self.CalculatedTriggeringProperties : dict[str, NumericalProperty] = {}
    
    def TriggerSolver(self):
        self.Owner.Solve()

    def TryAddToCalcQueue(self, forgetting):
        if forgetting:
            return self.Owner.StaticsSolver.TryAddObjectToForgettingQueue(self)
        else:
            return self.Owner.StaticsSolver.TryAddObjectToSolvingQueue(self)
        
    def ClearCalculatedProperties(self):
        for prop in self.CalculatedTriggeringProperties.values():
            if prop.Owner.Id != self.Id:
                self.Owner.StaticsSolver.TryAddObjectToForgettingQueue(prop.Owner)
            prop.Clear()
        
        self.CalculatedTriggeringProperties.clear()

    @abstractmethod
    def Calculate(self, IsForgetting: bool):
        pass

    @abstractmethod 
    def VariableChanging(self, Variable : NumericalProperty):
        pass

    @abstractmethod
    def VariableChanged(self, Variable : NumericalProperty):
        pass

# My class 
'''
class Cell:

    CalcOrder : int

    def __init__(self, name, SimCase: Flowsheet, calcOrder = 500):
        self.NumberofColums = 5
         
        self.ImportedVeriable : NumericalProperty = None
'''


class DummyUnitOp(BaseUnitOp):

    CalcOrder : int

    def __init__(self, name, SimCase: Flowsheet, calcOrder = 500):
        super().__init__(name, SimCase, calcOrder)
        self.PressureIn = NumericalProperty("PressureIn", UnitTypeEnum.PRESSURE, self, True, None)
        self.PressureOut = NumericalProperty("PressureOut", UnitTypeEnum.PRESSURE, self, True, None)
        self.PressureDrop = NumericalProperty("dP", UnitTypeEnum.DELTA_P, self, True, None)
        self.TemperatureIn = NumericalProperty("TemperatureIn", UnitTypeEnum.TEMPERATURE, self, True, None)
        self.TemperatureOut = NumericalProperty("TemperatureOut", UnitTypeEnum.TEMPERATURE, self, True, None)
        self.TemperatureDrop = NumericalProperty("dT", UnitTypeEnum.DELTA_T, self, True, None)
        self.pressureFlag = False
        self.temperatureFlag = False
        #self.NumberOfRows = NumericalProperty("RowsNumber", UnitTypeEnum.INDEX, self, True, None, 10)
        #self.NumberOfColumns = NumericalProperty("ColumnsNumber", UnitTypeEnum.INDEX, self, True, None,  10)


    def __lt__(self, other):
        return self.CalcOrder < other.CalcOrder
    

    def Calculate(self, IsForgetting: bool):
        self.IsCalculated = False

        if IsForgetting:
            self.pressureFlag = False
            self.temperatureFlag = False
            return True

        # Calculate UnitOp
        if not self.pressureFlag:
            self.pressureFlag = self.Balance(self.PressureIn, self.PressureOut, self.PressureDrop) 

        if not self.temperatureFlag:
            self.temperatureFlag = self.Balance(self.TemperatureIn, self.TemperatureOut, self.TemperatureDrop)

        self.IsCalculated = self.pressureFlag and self.temperatureFlag
        return self.IsCalculated


    def VariableChanging(self, Variable : NumericalProperty):

        if Variable.NewValue < 0 : return False
        return True

    def VariableChanged(self, Variable : NumericalProperty):
        pass

    def Balance(self, larger_property : NumericalProperty, smaller_property : NumericalProperty, delta : NumericalProperty):
        if smaller_property.HasValue and larger_property.HasValue:
            delta.Calculate(larger_property.Value - smaller_property.Value, self)
            return True
        elif smaller_property.HasValue and delta.HasValue:
            larger_property.Calculate(smaller_property.Value + delta.Value, self)
            return True
        elif larger_property.HasValue and delta.HasValue:
            smaller_property.Calculate(larger_property.Value - delta.Value, self)
            return True
        return False


# my Spreadsheet 
class Spreadsheet(BaseUnitOp):
    
    def __init__(self, y, x, name, SimCase: Flowsheet):
        super().__init__(name, SimCase, calcOrder = 500)
        #self.NumberOfRows : NumericalProperty = x
        self.x = x
        self.y = y
        self.Table = np.empty(shape=(self.y, self.x), dtype =  Cell )
        for i in range(y):
            for j in range (x):
                self.Table[i][j] = Cell("TestCell")
        
        # для ф измен. разм.
        self.NumberOfRows_y = y
        self.NumberOfColums_x = x


        #  !!! [y][x] = [rows][colums]

    def NumberOfRows (self, send):
        if type(round(send)) == int:
            new  =  int(send)
            self.Table.resize((new, self.NumberOfColums_x),  refcheck= False)
            
            # filling in new cells
            if new > self.NumberOfRows_y:
                for i in range(self.NumberOfRows_y - 1, new):
                    for j in range (self.NumberOfColums_x):
                        self.Table[i][j] =  Cell("TestCell")
            
            self.NumberOfRows_y = new
            return True
        else:
            print("wrong tipe")
            return False
       
    def NumberOfColums (self, send):

        if type(round(send)) == int:
            new  =  int(send)
            #self.Table.resize((self.NumberOfRows_y, new),  refcheck= False)
            #self.Table.append(self.Table, np.zeros([len(b), new]),1)
            '''
            # filling in new cells
            if new > self.NumberOfColums_x:
                for i in range(self.NumberOfRows_y):
                    for j in range(self.NumberOfColums_x - 1, new):
                        self.Table[i][j] =  Cell("TestCell")
            '''
                        
            self.NumberOfColums_x = new
            return True
        else:
            print("wrong tipe")
            return False
    
    def PrintTable(self):
        for i in range(0, len(self.Table)):
            for i2 in range(0, len(self.Table[i])):
                print(self.Table[i][i2], end=' ')
       
class Cell:
    def __init__(self, name, calcOrder = 500):
        self.ImportedVariable : NumericalProperty = None
        self.ExportVariable : NumericalProperty = None
        self.CalcOder = calcOrder


if __name__ == '__main__':
    
    # Create flowsheet
    Flwsht  = Flowsheet()

    # Add Unitops
    TestUO = DummyUnitOp("TestUO", Flwsht)

    # Set Specifications
    TestUO.PressureIn.SetValue(200,"kPa")
    pressureIn = TestUO.PressureIn.GetValue("kPa")


    #TestUO.PressureDrop.SetValue(100,"kPa")
    TestUO.TemperatureIn.SetValue(10,"C")
    TestUO.TemperatureDrop.SetValue(5,"C")

    

    {
    # Add UnitOps
    # for i in range(10):
    #     random_number = random.randint(0, 100)
    #     TestUO = DummyUnitOp(f"TestUO{i}", Flwsht, random_number)
    #     # Why does its not working ????????????
    #     #Flwsht.ItemsDict[f"TestUO{i}"].CalcOrder = i
    #     #TestUO.CalcOrder = i
    #     # Set Specifications
    #     TestUO.PressureIn.SetValue(200 + i,"kPa")
    #     TestUO.PressureDrop.SetValue(100 + i,"kPa")
    #     TestUO.TemperatureIn.SetValue(10 + i,"C")
    #     TestUO.TemperatureDrop.SetValue(5 + i,"C")
    }

 
    # Start Solver
    Flwsht.ActivateSolver()

    #--->
    '''
    #что я должен реализовать
    Spr = Spreadsheet(x,y)
    Spr.Cell(0,0).ImportVariable = TestUO.TemperatureIn
    Spr.Cell(0,1).ExportVariable = TestUO.PressureIn

    Spr.Cell(0,1).ExportVariable.SetValue(300, 'MPa')


    '''
    #<---

    #>>>
    #моя реализация
    Spr = Spreadsheet(3, 3, "Spreadsheet1", Flwsht)
    #Spr.Table[0][0] = Cell("TestCell", Flwsht)
    Spr.Table[0][0].ImportedVariable = TestUO.PressureIn  
    Spr.Table[0][0].ImportedVariable.SetValue(700,"kPa")

    '''
    Spr.Table[9][9] = Cell("TestCell", Flwsht)
    Spr.Table[9][9].ImportedVariable = TestUO.PressureIn
    Spr.Table[9][9].ImportedVariable.SetValue(500,"kPa")  
    print(Spr.Table[0][0].ImportedVariable.GetValue("kPa"))
    '''
    
    #Spr.PrintTable()
    #NumberOfRows(-1)

    #Spr.NumberOfRows2(15)

    #print(Spr.Table)

    #Spr.NumberOfRows(8)
    #Spr.NumberOfColums(7)

    #Spr.NumberOfRow.Setvalue(12SS)
    #Spr.Table.resize(2,4, refcheck= False)
    #Spr.Table.resize(10,10, refcheck = False)

    
    print(Spr.Table)

    b = np.array([[1.5, 2, 3], [4, 5, 6],[4, 5, 6]])
    #b.resize((1, 3),  refcheck= False)
    #b = np.append(b, np.zeros([len(b),2]),1)
    #b.resize((1, 4),  refcheck= False)
    #b = np.append(b, np.zeros([1,len(b)]),1)
    b  = b[0:-1]
    print(b)


    #print(Spr.Table[9][0])

    #print(Spr.NumberOfColumns.GetValue())
  

    #--->
    #пример как ссылаться на класс
    '''
    Massive =  np.empty(shape = (2,3), dtype= NumericalProperty)
    Massive[0][0] = TestUO.PressureIn
    print((Massive[0][0]).GetValue("kPa"))
    '''
    #<---

    #--->
    '''
    #Риализация Сell
    cellTest = Cell("TestCell", Flwsht)
    cellTest.ImportedVeriable = TestUO.PressureIn  
    '''  
    #<---

    #<<<
    #--->>
    '''
    # попытка реализации    
    import numpy as np

    #temp = pressureIn 
    #создание матрицы 
    m = np.empty(shape=(2, 2), dtype = object )
    #np.resize(a,(2,3))
    #prIn =  [pressureIn]

    #перессылка 
    prIn =  TestUO.PressureIn.NewVal
    m[0][0]= prIn
    
    # внешнее изменение 
    TestUO.PressureIn.SetValue(500,"kPa")

    #проверка
    print(m[0][0])
    print(prIn)
    '''


    #<<---

    '''
    TestUO.PressureOut.SetValue(m[0][0],"kPa")
    #m[0][0] = 400
    pressureOut = TestUO.PressureOut.GetValue("kPa")
    print(pressureOut)
    '''

    #<<---



    # Analyze sim case state
    a = 0
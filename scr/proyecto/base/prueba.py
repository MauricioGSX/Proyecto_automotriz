#Codigo muy avanzado para ti zicko esto no es del proyecto pero me da paja eliminarlo ya 

def es_bisiesto(año):
    return año % 4 == 0 and (año % 100 != 0 or año % 400 == 0)

def diferencia(YYYYMMDD, AAAAMmDd):
    assert type(YYYYMMDD) == int and type(AAAAMmDd) == int
    assert 1 <= YYYYMMDD <= 99991231 and 1 <= AAAAMmDd <= 99991231           
    YYYY = YYYYMMDD // 10000
    AAAA = AAAAMmDd // 10000 
    assert YYYY >= 1 and AAAA >= 1
    MM = (YYYYMMDD // 100) % 100
    Mm = (AAAAMmDd // 100) % 100                                                      
    assert 1 <= MM <= 12 and 1 <= Mm <= 12     
    DD = YYYYMMDD % 100
    Dd = AAAAMmDd % 100
    assert 1 <= DD <= 31 and 1 <= Dd <= 31

    YearD = abs(YYYY - AAAA) * 365

    MonthD = abs(MM - Mm) * 30
    if MonthD == 2:
        return 58

    DayD = abs(DD - Dd)

    bisiestos_cuenta = 0
    nobisiestos_cuenta = 0

    for año in range(min(YYYY, AAAA), max(YYYY, AAAA) + 1):
        if es_bisiesto(año):
            bisiestos_cuenta += 1
        else:
            nobisiestos_cuenta += 1

    FechaBisiestos = (YearD + MonthD + DayD + bisiestos_cuenta) // 366
    FechaNoBisiestos = (YearD + MonthD + DayD + nobisiestos_cuenta) // 365

    return FechaBisiestos, FechaNoBisiestos

resultado_bisiestos, resultado_nobisiestos = diferencia(20140225, 20210516)



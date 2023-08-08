import source.indicator_testing as indicator_testing

def is_leap_year(year):
    if (year % 400 == 0):
        return True
    elif (year % 100 == 0):
        return False
    elif (year % 4 == 0):
        return True
    return False

def test_may_aug(coin, filename, year):
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="05/01/" + str(year) + " 00:00:00", end_day="05/08/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="05/08/" + str(year) + " 00:00:00", end_day="05/15/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="05/15/" + str(year) + " 00:00:00", end_day="05/22/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="05/22/" + str(year) + " 00:00:00", end_day="05/29/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="05/29/" + str(year) + " 00:00:00", end_day="06/05/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="06/05/" + str(year) + " 00:00:00", end_day="06/12/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="06/12/" + str(year) + " 00:00:00", end_day="06/19/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="06/19/" + str(year) + " 00:00:00", end_day="06/26/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="06/26/" + str(year) + " 00:00:00", end_day="07/03/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="07/03/" + str(year) + " 00:00:00", end_day="07/10/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="07/10/" + str(year) + " 00:00:00", end_day="07/17/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="07/17/" + str(year) + " 00:00:00", end_day="07/24/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="07/24/" + str(year) + " 00:00:00", end_day="07/31/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="07/31/" + str(year) + " 00:00:00", end_day="08/07/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="08/07/" + str(year) + " 00:00:00", end_day="08/14/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="08/14/" + str(year) + " 00:00:00", end_day="08/21/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="08/21/" + str(year) + " 00:00:00", end_day="08/28/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="08/28/" + str(year) + " 00:00:00", end_day="09/01/" + str(year) + " 00:00:00", csv_filename=filename)

def test_jan_apr(coin, filename, year):
    if is_leap_year(year) == True:
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/01/" + str(year) + " 00:00:00", end_day="01/08/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/08/" + str(year) + " 00:00:00", end_day="01/15/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/15/" + str(year) + " 00:00:00", end_day="01/22/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/22/" + str(year) + " 00:00:00", end_day="01/29/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/29/" + str(year) + " 00:00:00", end_day="02/05/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="02/05/" + str(year) + " 00:00:00", end_day="02/12/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="02/12/" + str(year) + " 00:00:00", end_day="02/19/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="02/19/" + str(year) + " 00:00:00", end_day="02/26/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="02/26/" + str(year) + " 00:00:00", end_day="03/04/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="03/04/" + str(year) + " 00:00:00", end_day="03/11/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="03/11/" + str(year) + " 00:00:00", end_day="03/18/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="03/18/" + str(year) + " 00:00:00", end_day="03/25/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="03/25/" + str(year) + " 00:00:00", end_day="04/01/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/01/" + str(year) + " 00:00:00", end_day="04/08/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/08/" + str(year) + " 00:00:00", end_day="04/15/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/15/" + str(year) + " 00:00:00", end_day="04/22/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/22/" + str(year) + " 00:00:00", end_day="04/29/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/29/" + str(year) + " 00:00:00", end_day="05/01/" + str(year) + " 00:00:00", csv_filename=filename)
    else:
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/01/" + str(year) + " 00:00:00", end_day="01/08/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/08/" + str(year) + " 00:00:00", end_day="01/15/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/15/" + str(year) + " 00:00:00", end_day="01/22/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/22/" + str(year) + " 00:00:00", end_day="01/29/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="01/29/" + str(year) + " 00:00:00", end_day="02/05/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="02/05/" + str(year) + " 00:00:00", end_day="02/12/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="02/12/" + str(year) + " 00:00:00", end_day="02/19/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="02/19/" + str(year) + " 00:00:00", end_day="02/26/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="02/26/" + str(year) + " 00:00:00", end_day="03/05/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="03/05/" + str(year) + " 00:00:00", end_day="03/12/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="03/12/" + str(year) + " 00:00:00", end_day="03/19/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="03/19/" + str(year) + " 00:00:00", end_day="03/26/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="03/26/" + str(year) + " 00:00:00", end_day="04/02/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/02/" + str(year) + " 00:00:00", end_day="04/09/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/09/" + str(year) + " 00:00:00", end_day="04/16/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/16/" + str(year) + " 00:00:00", end_day="04/23/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="04/23/" + str(year) + " 00:00:00", end_day="05/01/" + str(year) + " 00:00:00", csv_filename=filename)

def test_sep_dec(coin, filename, year):
    if (year > 2019):
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="09/01/" + str(year) + " 00:00:00", end_day="09/08/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="09/08/" + str(year) + " 00:00:00", end_day="09/15/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="09/15/" + str(year) + " 00:00:00", end_day="09/22/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="09/22/" + str(year) + " 00:00:00", end_day="09/29/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="09/29/" + str(year) + " 00:00:00", end_day="10/06/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="10/06/" + str(year) + " 00:00:00", end_day="10/13/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="10/13/" + str(year) + " 00:00:00", end_day="10/20/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="10/20/" + str(year) + " 00:00:00", end_day="10/27/" + str(year) + " 00:00:00", csv_filename=filename)
        indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="10/27/" + str(year) + " 00:00:00", end_day="11/03/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="11/03/" + str(year) + " 00:00:00", end_day="11/10/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="11/10/" + str(year) + " 00:00:00", end_day="11/17/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="11/17/" + str(year) + " 00:00:00", end_day="11/24/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="11/24/" + str(year) + " 00:00:00", end_day="12/01/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="12/01/" + str(year) + " 00:00:00", end_day="12/08/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="12/08/" + str(year) + " 00:00:00", end_day="12/15/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="12/15/" + str(year) + " 00:00:00", end_day="12/22/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="12/22/" + str(year) + " 00:00:00", end_day="12/29/" + str(year) + " 00:00:00", csv_filename=filename)
    indicator_testing.optimize_BB_optimize_RSI(symbol=coin, start_day="12/29/" + str(year) + " 00:00:00", end_day="01/01/" + str(year + 1) + " 00:00:00", csv_filename=filename)

if __name__ == "__main__":
    test_jan_apr("BTC", "btc_testing_weeks_jan_apr_2020.csv", 2020)
    test_may_aug("BTC", "eth_testing_weeks_may_aug_2020.csv", 2020)

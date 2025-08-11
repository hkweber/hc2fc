

cyc_count = [1,2,2,1,1,2,2,3,4]

out = [1,2,2,3,3,4,4,5,6,7]

def calc_abs_cycle (cyc_count):
    # Calculates abs_cycle from cyc_count

    expected_cycle = 1
    last_cycle = 1
    cycle = []

    for cyc in cyc_count:
        if cyc == expected_cycle:
            cycle.append(expected_cycle)

        else:
            if cyc !=last_cycle:
                expected_cycle = expected_cycle +1
                cycle.append(expected_cycle)
            else:
                cycle.append(expected_cycle)
        last_cycle = cyc

    return cycle

print(calc_abs_cycle(cyc_count))     
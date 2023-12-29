from pulp import LpMinimize, LpProblem, LpStatus, LpVariable, lpSum

N_DOCTORS = 10
DAYS = [1, 2, 3, 4, 5]
HOLIDAYS = [6, 7]


def main() -> None:
    # Create a problem
    prob = LpProblem("HospitalAllocation", LpMinimize)

    # Define decision variables
    # Let x[i, j] be the amount of doctors i allocated to task j
    n_doctors = 10
    doctors = [f"d_{i}" for i in range(n_doctors + 1)]

    # tasks
    ward = [f"ward_{i}" for i in DAYS]
    nursery = [f"nursery_{i}" for i in DAYS]
    surgery_morning = [f"surgery_morning_{i}" for i in DAYS]
    surgery_afternoon = [f"surgery_afternoon_{i}" for i in DAYS]
    night = [f"night_{i}" for i in DAYS]
    night_holiday = [f"night_holiday_{i}" for i in HOLIDAYS]
    surgery_holiday = [f"surgery_holiday{i}" for i in HOLIDAYS]

    tasks = (
        ward
        + nursery
        + surgery_morning
        + surgery_afternoon
        + night
        + night_holiday
        + surgery_holiday
    )

    x = LpVariable.dicts(
        "allocation",
        [(i, j) for i in doctors for j in tasks],
        lowBound=0,
        cat="Integer",
    )
    # cost of each task
    cost_4 = dict.fromkeys([(r, t) for r in doctors for t in surgery_morning], 4)
    cost_8 = dict.fromkeys(
        [(r, t) for r in doctors for t in ward + nursery + surgery_afternoon], 8
    )
    cost_12 = dict.fromkeys(
        [(r, t) for r in doctors for t in night + night_holiday + surgery_holiday], 12
    )
    cost = {**cost_4, **cost_8, **cost_12}

    # minimize total cost
    prob += lpSum(x[i, j] * cost[i, j] for i in doctors for j in tasks)

    # Define constraints
    # Ensure that each task gets the required amount of doctors
    for j in tasks:
        prob += lpSum(x[i, j] for i in doctors) == 1

    # Ensure that the total amount of each resource does not exceed its capacity

    # d1->5: 100% (40 h)
    time_100 = dict.fromkeys([f"d_{i}" for i in range(0, 5 + 1)], 40)
    # d6->8: 75% (30 h)
    time_75 = dict.fromkeys([f"d_{i}" for i in range(6, 8 + 1)], 30)
    # d9->10: 50% (20 h)
    time_50 = dict.fromkeys([f"d_{i}" for i in range(9, 10 + 1)], 20)

    resource_capacity = {**time_100, **time_75, **time_50}

    for i in doctors:
        prob += lpSum(x[i, j] for j in tasks) <= resource_capacity[i]

    # Solve the problem
    prob.solve()

    # Print the results
    print("Status:", LpStatus[prob.status])

    for v in prob.variables():
        print(v.name, "=", v.varValue)


if __name__ == "__main__":
    main()

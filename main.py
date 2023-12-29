import pandas as pd
from pulp import LpMinimize, LpProblem, LpStatus, LpVariable, lpSum

N_DOCTORS = 10
DAYS = [1, 2, 3, 4, 5]
HOLIDAYS = [6, 7]


def main() -> None:
    # Create an optimization problem (minimization)
    prob = LpProblem("HospitalAllocation", LpMinimize)

    # -------- DECISION VARIABLES ---------------

    # doctors
    doctors = [f"d{str(i).zfill(2)}" for i in range(N_DOCTORS + 1)]
    # tasks
    ward = [f"t{i}Ward" for i in DAYS]
    nursery = [f"t{i}Nursery" for i in DAYS]
    surgery_morning = [f"t{i}SurgeryMorning" for i in DAYS]
    surgery_afternoon = [f"t{i}SurgeryAfternoon" for i in DAYS]
    night = [f"t{i}Night" for i in DAYS]
    night_holiday = [f"t{i}NightHoliday" for i in HOLIDAYS]
    surgery_holiday = [f"t{i}SurgeryHoliday" for i in HOLIDAYS]

    tasks = (
        ward
        + nursery
        + surgery_morning
        + surgery_afternoon
        + night
        + night_holiday
        + surgery_holiday
    )
    # Let x[i, j] be the amount of doctors i allocated to task j
    x = LpVariable.dicts(
        "allocation",
        [(i, j) for i in doctors for j in tasks],
        lowBound=0,
        cat="Integer",
    )
    # -------- OBJECTIVE FUNCTION ---------------

    # cost (time) of each task
    cost_4 = dict.fromkeys([(r, t) for r in doctors for t in surgery_morning], 4)
    cost_8 = dict.fromkeys(
        [(r, t) for r in doctors for t in ward + nursery + surgery_afternoon], 8
    )
    cost_12 = dict.fromkeys(
        [(r, t) for r in doctors for t in night + night_holiday + surgery_holiday], 12
    )
    cost = {**cost_4, **cost_8, **cost_12}

    # minimize total cost (time)
    prob += lpSum(x[i, j] * cost[i, j] for i in doctors for j in tasks)

    # -------- CONSTRAINTS ---------------

    # Each task must be covered by 1 doctor
    for j in tasks:
        prob += lpSum(x[i, j] for i in doctors) == 1

    # Each doctor must not exceed the maximum number of hours per week

    # doctors 1->5: 100% (40 h)
    time_100 = dict.fromkeys([f"d{str(i).zfill(2)}" for i in range(0, 5 + 1)], 40)
    # doctors 6->8: 75% (30 h)
    time_75 = dict.fromkeys([f"d{str(i).zfill(2)}" for i in range(6, 8 + 1)], 30)
    # doctors 9->10: 50% (20 h)
    time_50 = dict.fromkeys([f"d{str(i).zfill(2)}" for i in range(9, 10 + 1)], 20)

    resource_capacity = {**time_100, **time_75, **time_50}

    for i in doctors:
        prob += lpSum(x[i, j] for j in tasks) <= resource_capacity[i]

    # -------- SOLUTION ---------------

    # Solve the problem
    prob.solve()

    # Print the results
    print("Status:", LpStatus[prob.status])
    df = pd.DataFrame()
    for v in prob.variables():
        doctor, task = v.name.replace("(", "").replace(")", "").split("_")[1:]
        df.loc[doctor, task] = v.varValue
        # print(doctor, task, v.varValue)
        # print(v.name, "=", v.varValue)
    df = df.astype("Int8")
    df.to_csv("solution.csv", sep=";", index=True)


if __name__ == "__main__":
    main()

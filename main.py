import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pulp import LpMinimize, LpProblem, LpStatus, LpVariable, lpSum

N_DOCTORS = 10
DAYS = [
    1,
    2,
    3,
    4,
    5,
    8,
    9,
    10,
    11,
    12,
    15,
    16,
    17,
    18,
    19,
    22,
    23,
    24,
    25,
    26,
    29,
    30,
    31,
]
HOLIDAYS = [6, 7, 13, 14, 20, 21, 27, 28]


def main() -> None:
    # Create an optimization problem (minimization)
    prob = LpProblem("HospitalAllocation", LpMinimize)

    # -------- DECISION VARIABLES ---------------

    # doctors
    doctors = [f"d{str(i).zfill(2)}" for i in range(N_DOCTORS)]
    # tasks
    ward = [f"t{str(i).zfill(2)}Ward" for i in DAYS]
    nursery = [f"t{str(i).zfill(2)}Nursery" for i in DAYS]
    surgery_morning = [f"t{str(i).zfill(2)}SurgeryMorning" for i in DAYS]
    surgery_afternoon = [f"t{str(i).zfill(2)}SurgeryAfternoon" for i in DAYS]
    night = [f"t{str(i).zfill(2)}Night" for i in DAYS]
    night_holiday = [f"t{str(i).zfill(2)}Night" for i in HOLIDAYS]
    surgery_holiday = [f"t{str(i).zfill(2)}Surgery" for i in HOLIDAYS]

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
    cost_4 = dict.fromkeys([t for t in surgery_morning], 4)
    cost_8 = dict.fromkeys([t for t in ward + nursery + surgery_afternoon], 8)
    cost_12 = dict.fromkeys([t for t in night + night_holiday + surgery_holiday], 12)
    cost = {**cost_4, **cost_8, **cost_12}

    # minimize total cost (time)
    prob += lpSum(x[i, j] * cost[j] for i in doctors for j in tasks)

    # -------- CONSTRAINTS ---------------

    # Each task must be covered by 1 doctor
    for j in tasks:
        prob += lpSum(x[i, j] for i in doctors) == 1

    # doctors 100% (40 h)
    time_100 = dict.fromkeys([f"d{str(i).zfill(2)}" for i in range(0, 5 + 1)], 160)
    # doctors  75% (30 h)
    time_75 = dict.fromkeys([f"d{str(i).zfill(2)}" for i in range(6, 8 + 1)], 120)
    # doctors 50% (20 h)
    time_50 = dict.fromkeys([f"d{str(i).zfill(2)}" for i in range(9, 10 + 1)], 80)

    resource_capacity = {**time_100, **time_75, **time_50}

    for i in doctors:
        # Each doctor must not exceed the maximum number of hours per week
        prob += lpSum(x[i, j] * cost[j] for j in tasks) <= resource_capacity[i]
        # Each doctor cannot do multiple tasks in the same day
        max_day = max(DAYS + HOLIDAYS)
        for day in range(1, max_day + 1):
            tasks_day = [t for t in tasks if t.startswith(f"t{str(day).zfill(2)}")]
            prob += lpSum(x[i, j] for j in tasks_day) <= 1
        # night shift ("smonto notte")
        for day in range(2, max_day + 1):  # starting from day 2
            tasks_day_light = [
                t
                for t in tasks
                if t.startswith(f"t{str(day).zfill(2)}")
                and t != f"t{str(day).zfill(2)}Night"
            ]
            night_actual = [f"t{str(day).zfill(2)}Night"]
            night_before = [f"t{str(day-1).zfill(2)}Night"]
            prob += lpSum(x[i, j] for j in tasks_day_light + night_before) <= 1
            prob += lpSum(x[i, j] for j in night_actual + night_before) <= 1

    # -------- SOLUTION ---------------

    # Solve the problem
    prob.solve()

    # Print the results
    status = LpStatus[prob.status]
    print(f"{status=}")
    if status == "Infeasible":
        print("No solution")
        return
    res = {}
    for v in prob.variables():
        doctor, task = v.name.replace("(", "").replace(")", "").split("_")[1:]
        res[(doctor, task)] = v.varValue
    df = pd.DataFrame(list(res.keys()), columns=["Doctor", "Task"])
    df["Value"] = list(res.values())
    df["Day"] = df["Task"].str[:4]
    df["Task"] = df["Task"].str[4:]
    df = df[df["Value"] == 1]
    df_pivot_1 = df.pivot(index="Day", columns="Task", values="Doctor")
    df_pivot_1.to_csv(f"solution_tasks.csv", sep=";", index=True)
    df_pivot_2 = df.pivot(index="Day", columns="Doctor", values="Task")
    df_pivot_2.to_csv(f"solution_doctors.csv", sep=";", index=True)

    stats = df.groupby(["Doctor", "Task"])["Value"].sum().reset_index()
    plt.figure(figsize=(10, 4))
    sns.barplot(data=stats, x="Doctor", y="Value", hue="Task")
    plt.savefig("stats.png")


if __name__ == "__main__":
    main()

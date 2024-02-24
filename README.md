# hospital-allocation

Optimization tool for resource allocation of medical specialists in a hospital (monthly shifts).

## Problem

Assign the shifts for each doctor respecting the following constraints:
- Shifts must be covered by one and only one doctor.
- Doctors must not exceed the maximum number of hours per week, based on their contract (full time or part-time).
- Doctors can not do multiple shifts in the same day.
- Night shifts rules: 1. two consecutive night shifts are not allowed 2. day shifts before and after the night are not allowed.
- Holydays / week-ends.

## Solution

Integer Linear Programming using [PuLP](https://coin-or.github.io/pulp/) (python library) and [CBC](https://www.coin-or.org/Cbc/cbcuserguide.html) (COIN-OR Branch and Cut) solver.
The goal is to minimize the cumulative work hours for each doctor while ensuring that all constraints are met.

## Output

3 solution views available:
- solution_doctors.csv: table with tasks assigned to each doctor, every day
- solution_tasks.csv: table with doctors assigned to each task, every day
- stats.png: plot with distribution of shifts for each doctor

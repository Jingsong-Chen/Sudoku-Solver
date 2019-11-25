Assignment 5: Sudoku
=========

Due date
-----
March-17 (Sunday) 11:59pm Pacific Time. 

Tasks (14 Points)
-----
- Documentation (1 Point)

- Sudoku Solver (13 Points)

Implement a Sudoku solver based on techniques explained in [this post](http://norvig.com/sudoku.html). Feel free to learn from the code but need to adapt it without changing the data structures in the given starter code in `sudoku.py`. You can change the function signatures in the Solver class if you like (and add more functions of course). 

We will test your solver on benchmarks in `easy_sudoku_problems.txt` and `hard_sudoku_problems.txt`. 

Extra credits (6 Points)
-----
- Hexadoku Solver (1 Point)

Modify the code (create a new file `hexadoku.py`) to solve Hexadoku problems. You can find such problems [here](https://www.sudoku-puzzles-online.com/hexadoku/choose-hexadoku-grid.php) and choose 2 simple problems to be benchmarks (in the format of Line 47 in the `sudoku.py` file). 

- Sudoku with SAT (4 Points)

Implement an encoding of Sudoku as propositional logic formulas in conjunctive normal forms, and use a state-of-the-art SAT solver to solve. Read the `notes.pdf` file for more details. The `hard1.cnf` file in the `cnf` directory is the encoding of the first hard instance in the code. You need to generate the CNF files, pass them to a SAT solver (see below) to solve, and then parse the output from the SAT solver and plug them back into the original problem and display the solutions. 

SAT Solvers to Use: I recommend [PicoSAT](http://fmv.jku.at/picosat/) as the default choice. Go to its webpage, download, and compile (simply do `./configure.sh` and then `make`). The binary `picosat` can then take the CNF files you produce (always use extension `.cnf`). I highly recommend that you find a linux/mac machine to use the solver. If you have to use windows, this [note](https://gist.github.com/ConstantineLignos/4601835) may be helpful but I haven't tried. If you have difficulty in getting PicoSAT to work, try [cryptominisat](https://github.com/msoos/cryptominisat) which has more instructions about making things work on windows. If you want to know about more SAT solvers, check the [page](http://www.satcompetition.org/) for the annual SAT solver competition. 


- Hexadoku with SAT (1 Point)

Extend the SAT encoding of Sudoku to Hexaduko and solve the problems in `hexadoku_problems.txt`. 


Files to submit
-----
Just `sudoku.py`. For the extra credit parts: `hexadoku.py`, `sudoku-with-sat.py`, `hexadoku-with-sat.py`. In grading we will assume an executable SAT solver named `picosat` can be used from the parent directory of these files (i.e., make your path to SAT solver to be `../picosat`). 


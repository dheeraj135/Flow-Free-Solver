## Flow Free Solver

### Required Conditions:
1. Each grid box have exactly one color.
2. We can have a grid of size N * M * num_colors * type.
3. We have two types of nodes, Endpoint and Connection Node.
4. We need seperate grid for each color because we can only store boolean value in SAT.
5. Now, we can have the end points as connected.
6. For now, let's assume only one pair of color exists.
7. Now, we need to write condition for connected wires.

### Conditions for the connected Wires:
1. Please find the conditions here: https://mzucker.github.io/2016/09/02/eating-sat-flavored-crow.html

Right Now I am not clearing up invalid loops. I don't understand how we can remove loops using N^2 additionals variables. I am thinking about solving it using incremental algorithm similiar to what I did in the mastermind problem.

### Future Plans:
1. GUI or React.js based frontend to simplify and beautify the input-output process.
2. Remove the loops.

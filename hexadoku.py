from __future__ import print_function
import random, copy


class Grid:
    def __init__(self, problem):
        # create an empty grid
        self.spots = [(i, j) for i in range(1, 17) for j in range(1, 17)]
        self.domains = {}       # all the possible values for each state
        self.peers = {}     # dictionary that maps each spot to its peers
        self.parse(problem)     # read the i
        # nitial layout from a problem

    # all the index in this program starts from 1
    def parse(self, problem):
        # iterate through the rows
        for i in range(0, 16):
            # iterate through each elements in each row
            for j in range(0, 16):
                # create unique identifiers for each tile
                c = problem[i * 16 + j]
                # if the tile is blank, it has 15 possible values, namely 1 - 15
                if c == '.':
                    self.domains[(i + 1, j + 1)] = range(0, 16)
                # if the tile has a number, then it only has one possible value
                else:
                    # if the digit is a HEX digit
                    if ord(c) >= 65:
                        self.domains[(i + 1, j + 1)] = [ord(c) - 65 + 10]
                    # if the digit is a decimal digit
                    else:
                        self.domains[(i + 1, j + 1)] = [ord(c) - 48]

    def display(self):
        for i in range(0, 16):
            for j in range(0, 16):
                # get all the possible values for a tile
                d = self.domains[(i + 1, j + 1)]
                # only display it when its value is definite
                if len(d) == 1:
                    if d[0] >= 10:
                        print(chr(d[0] - 10 + 65), end='')
                    else:
                        print(d[0], end='')
                # leave it blank if its value is not fixed
                else:
                    print('.', end='')
                # print the separators for visual effects
                if j == 3 or j == 7 or j == 11:
                    print(" | ", end='')
            print()
            # print the borders
            if i == 3 or i == 7 or i == 11:
                print("-------------------------")


############################################################


class Solver:
    def __init__(self, grid):
        # sigma is the assignment function
        self.grid = grid
        self.solution = None
        self.rows = []
        self.cols = []
        self.houses = {}
        self.digits = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}

    def solve(self):
        spots = self.grid.spots
        domains = self.grid.domains
        # construct the peer list
        self.find_peers()
        # find the solution by backtracking and return it
        return self.backtracking_search(spots, domains)

    # build up the peer dictionary
    def find_peers(self):
        # there're 3 houses in a row
        for row in range(1, 5):
            # there're 3 houses in a column
            for col in range(1, 5):
                self.houses[(row, col)] = set()
                # there are 9 squares per house
                for row_offset in range(1, 5):
                    for col_offset in range(1, 5):
                        self.houses[(row, col)].add(((row - 1) * 4 + row_offset, (col - 1) * 4 + col_offset))
                self.houses[(row, col)] = list(self.houses[(row, col)])
        # group all the rows
        self.rows.append([])    # dummy row for index 0
        for row in range(1, 17):
            self.rows.append([])
            for col in range(1, 17):
                self.rows[row].append((row, col))
        # group all the columns
        self.cols.append([])  # dummy row for index 0
        for col in range(1, 17):
            self.cols.append([])
            for row in range(1, 17):
                self.cols[col].append((row, col))
        # find peers for each square
        for spot in self.grid.spots:
            self.grid.peers[spot] = set()
            # find all the peers in the same row
            self.grid.peers[spot] |= set(self.rows[spot[0]])
            # find all the peers in the same column
            self.grid.peers[spot] |= set(self.cols[spot[1]])
            # find all the peers that share the same house
            self.grid.peers[spot] |= set(self.houses[(int((spot[0] - 1) / 4 + 1), int((spot[1] - 1) / 4 + 1))])
            # do not include the spot itself
            self.grid.peers[spot].discard(spot)
            # convert to list
            self.grid.peers[spot] = list(self.grid.peers[spot])
        return

    # domains is a dictionary where the keys are spots and the values are lists ints
    # spots is a collection of 81 pairs each indicating a row and a column
    def backtracking_search(self, spots, domains):
        domain_stack = [[domains, (0, 0), 20]]
        # while there're more assignments to try
        while domain_stack:
            #print('++++++++++++++++++++')
            # list.pop returns the last appended element in the list. this is desired for DFS
            situation = domain_stack.pop()
            pruned_domains = situation[0]
            spot = situation[1]
            guess = situation[2]
            print('try', guess, 'for', spot)
            # if new guess is made, need to validate it
            if guess > 0:
                #print('try', guess, 'for', situation[1])
                # prune the branches that we don't need to try. gets an empty list if constrains is violated
                pruned_domains = self.prune_it(pruned_domains, spot)
            # if the current assignments don't violate any constraint
            if pruned_domains:
                #print('printed from back track')
                #self.display(pruned_domains)
                found_unsettled_square = False    # indicates if all the squares has a fixed value
                # look at every square
                for spot in sorted(pruned_domains, key=lambda key: len(pruned_domains[key])):
                    # if exists a square that is not settled
                    if len(pruned_domains[spot]) > 1:
                        # the solving process is not finished yet
                        found_unsettled_square = True
                        # possibility 1: the last value in the spot's domain doesn't work. remove it from the domain
                        copy_1 = copy.deepcopy(pruned_domains)
                        value_to_try = copy_1[spot].pop()
                        if len(copy_1[spot]) == 1:
                            domain_stack.append([copy_1, spot, copy_1[spot][0]])
                        else:
                            domain_stack.append([copy_1, spot, -1])
                        # possibility 2: the last value in the spot's domain doesn't work. then keep simulating on it
                        copy_2 = copy.deepcopy(pruned_domains)
                        copy_2[spot] = [value_to_try]
                        domain_stack.append([copy_2, spot, value_to_try])
                        # DFS make guess on the next unsettled square
                        break
                # end the algorithm if all the squares have a fixed value
                if not found_unsettled_square:
                    self.solution = pruned_domains
                    return True
        # if the problem is unsolvable, return the original domains
        self.solution = domains
        return False

    # remove all the branches tha we don't need to try.
    # return an empty list if there's an unresolvable conflict
    def prune_it(self, domains, spot):
        if spot[0]:
            spots = [spot]
        else:
            print('initial prune')
            spots = []
            for sp in self.grid.spots:
                if len(domains[sp]) == 1:
                    spots.append(sp)
        # keep pruning till no spot changes
        while spots:
            settled = spots.pop()
            settled_value = domains[settled][0]
            for peer in self.grid.peers[settled]:
                if settled_value in domains[peer]:
                    domains[peer].remove(settled_value)
                    if len(domains[peer]) == 1:
                        spots.append(peer)
                    # if after deleting the spot's value, one peer doesn't have an eligible value, prune
                    if not domains[peer]:
                        #self.display(domains)
                        #print('spot', peer, 'goes wrong.')
                        # print(pruned_domains[peer])
                        # returns an empty dictionary since
                        return {}

                # Rule No.2: if a number is missing in a square's peers' possible values, that is the square's value
                row_peers = list(self.rows[peer[0]])
                row_peers.remove(peer)
                covered = set()
                for peer_s_peer in row_peers:
                    covered = covered.union(set(domains[peer_s_peer]))
                demand = list(self.digits - covered)
                # it is impossible that a single square can cover all the values missing
                if len(demand) > 1:
                    return {}
                # if there's a single value that's not covered by the square's peers in a unit
                elif len(demand) == 1:
                    if demand != domains[peer]:
                        # if the square already has a settled value and it is different from that demanding value
                        if len(domains[peer]) == 1:
                            return {}
                        else:
                            domains[peer] = demand
                            spots.append(peer)
                col_peers = list(self.cols[peer[1]])
                col_peers.remove(peer)
                covered = set()  # covered is the set of all numbers that the other squares in a unit can cover
                for peer_s_peer in col_peers:
                    covered = covered.union(set(domains[peer_s_peer]))
                demand = list(self.digits - covered)
                # it is impossible that a single square can cover all the values missing
                if len(demand) > 1:
                    return {}
                # if there's a single value that's not covered by the square's peers in a unit
                elif len(demand) == 1:
                    if demand != domains[peer]:
                        # if the square already has a settled value and it is different from that demanding value
                        if len(domains[peer]) == 1:
                            return {}
                        else:
                            domains[peer] = demand
                            spots.append(peer)
                house_peers = list(self.houses[(int((peer[0] - 1) / 4 + 1), int((peer[1] - 1) / 4 + 1))])
                # print(peer)
                # print(self.houses[(int((peer[0] - 1) / 4 + 1), int((peer[1] - 1) / 4 + 1))])
                # print(len(self.houses[(int((peer[0] - 1) / 4 + 1), int((peer[1] - 1) / 4 + 1))]))
                house_peers.remove(peer)
                covered = set()  # covered is the set of all numbers that the other squares in a unit can cover
                for peer_s_peer in house_peers:
                    covered = covered.union(set(domains[peer_s_peer]))
                demand = list(self.digits - covered)
                # it is impossible that a single square can cover all the values missing
                if len(demand) > 1:
                    return {}
                # if there's a single value that's not covered by the square's peers in a unit
                elif len(demand) == 1:
                    if demand != domains[peer]:
                        # if the square already has a settled value and it is different from that demanding value
                        if len(domains[peer]) == 1:
                            return {}
                        else:
                            domains[peer] = demand
                            spots.append(peer)
        return domains

    def display(self, domains):
        for i in range(0, 9):
            for j in range(0, 9):
                # get all the possible values for a tile
                d = domains[(i + 1, j + 1)]
                # only display it when its value is definite
                if len(d) == 1:
                    print(d[0], end='')
                # leave it blank if its value is not fixed
                else:
                    print('.', end='')
                # print the separators for visual effects
                if j == 2 or j == 5:
                    print(" | ", end='')
            print()
            # print the borders
            if i == 2 or i == 5:
                print("---------------")


#################################################################

    def display(self):
        for i in range(0, 16):
            for j in range(0, 16):
                # get all the possible values for a tile
                d = self.domains[(i + 1, j + 1)]
                # only display it when its value is definite
                if len(d) == 1:
                    if d[0] >= 10:
                        print(chr(d[0] - 10 + 65), end='')
                    else:
                        print(d[0], end='')
                # leave it blank if its value is not fixed
                else:
                    print('.', end='')
                # print the separators for visual effects
                if j == 3 or j == 7 or j == 11:
                    print(" | ", end='')
            print()
            # print the borders
            if i == 3 or i == 7 or i == 11:
                print("-------------------------")

hard16 = [".D4F.....856.03..5...D9..4.A62..A..1...0..2.54F...8.B...D.E.9.....9C.....D.4.E......7CB...F.......0D...A3B"
          "..F87.....2E...7...C.0.....4..C......B....F.E..0......D.7.91..E5......6.52A8..F.B.0..946..1..D.E8.3"
          ".....183B..5..........3..C.0....F.6B......2..9C8.A1",
          "3.8E....1..C.B.A.75.A..1.D.8..9....AE5B..0...6.26.9...34..F.....01..5.6..3..E.....2..1D0......4..4B.F..7"
          ".....9..85.C3...E2.9.....F..2...0.D1.37.....8.....7.D..B..4.............A..3.0..6.....84..ED6C9.B..08....9"
          "....8....2C43.........8..6A..D50..7....C..2.F.",
          "1D.B.....7.....6.35A.C.F..E....0...02.4..5..C18A4....BD..2......28..B....F..4...5.......6....8..D1A..2C.0"
          ".7.........A...48...E0C7.36.9..8..2A..........D.A...3.........65.C..0BD.2E.4.80......7F6.79.0....5F...1.5"
          "...D1.2.0C.B...C.....9.13....8...23A......5..."]

for problem in hard16:
    print("====Problem====")
    g = Grid(problem)
    # Display the original problem
    g.display()
    s = Solver(g)

    s.find_peers()
    # for square, peers in s.grid.peers.iteritems():
    #     print(len(s.grid.peers[square]))

    if s.solve():
        print("====Solution===")
        # Display the solution
        # Feel free to call other functions to display
        s.display(s.solution)
    else:
        print("==No solution==")

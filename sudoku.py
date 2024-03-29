from __future__ import print_function
import random, copy


class Grid:
    def __init__(self, problem):
        # create an empty grid
        self.spots = [(i, j) for i in range(1, 10) for j in range(1, 10)]
        self.domains = {}       # all the possible values for each state
        self.peers = {}     # dictionary that maps each spot to its peers
        self.parse(problem)     # read the i
        # nitial layout from a problem

    # all the index in this program starts from 1
    def parse(self, problem):
        # iterate through the rows
        for i in range(0, 9):
            # iterate through each elements in each row
            for j in range(0, 9):
                # create unique identifiers for each tile
                c = problem[i * 9 + j]
                # if the tile is blank, it has 9 possible values, namely 1 - 9
                if c == '.':
                    self.domains[(i + 1, j + 1)] = range(1, 10)
                # if the tile has a number, then it only has one possible value
                else:
                    self.domains[(i + 1, j + 1)] = [ord(c) - 48]

    def display(self):
        for i in range(0, 9):
            for j in range(0, 9):
                # get all the possible values for a tile
                d = self.domains[(i + 1, j + 1)]
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


############################################################


class Solver:
    def __init__(self, grid):
        # sigma is the assignment function
        self.grid = grid
        self.solution = None
        self.rows = []
        self.cols = []
        self.houses = {}
        self.digits = {1, 2, 3, 4, 5, 6, 7, 8, 9}

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
        for row in range(1, 4):
            # there're 3 houses in a column
            for col in range(1, 4):
                self.houses[(row, col)] = set()
                # there are 9 squares per house
                for row_offset in range(1, 4):
                    for col_offset in range(1, 4):
                        self.houses[(row, col)].add(((row - 1) * 3 + row_offset, (col - 1) * 3 + col_offset))
                self.houses[(row, col)] = list(self.houses[(row, col)])
        # group all the rows
        self.rows.append([])    # dummy row for index 0
        for row in range(1, 10):
            self.rows.append([])
            for col in range(1, 10):
                self.rows[row].append((row, col))
        # group all the columns
        self.cols.append([])  # dummy row for index 0
        for col in range(1, 10):
            self.cols.append([])
            for row in range(1, 10):
                self.cols[col].append((row, col))
        # find peers for each square
        for spot in self.grid.spots:
            self.grid.peers[spot] = set()
            # find all the peers in the same row
            self.grid.peers[spot] |= set(self.rows[spot[0]])
            # find all the peers in the same column
            self.grid.peers[spot] |= set(self.cols[spot[1]])
            # find all the peers that share the same house
            self.grid.peers[spot] |= set(self.houses[(int((spot[0] - 1) / 3 + 1), int((spot[1] - 1) / 3 + 1))])
            # do not include the spot itself
            self.grid.peers[spot].discard(spot)
            # convert to list
            self.grid.peers[spot] = list(self.grid.peers[spot])
        return

    # domains is a dictionary where the keys are spots and the values are lists ints
    # spots is a collection of 81 pairs each indicating a row and a column
    def backtracking_search(self, spots, domains):
        domain_stack = [[domains, (0, 0), 10]]
        # while there're more assignments to try
        while domain_stack:
            #print('++++++++++++++++++++')
            # list.pop returns the last appended element in the list. this is desired for DFS
            situation = domain_stack.pop()
            pruned_domains = situation[0]
            spot = situation[1]
            guess = situation[2]
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
                house_peers = list(self.houses[(int((peer[0] - 1) / 3 + 1), int((peer[1] - 1) / 3 + 1))])
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


# easy = ["..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..",
#         "2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3"]
easy = ['..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..',
 '2...8.3...6..7..84.3.5..2.9...1.54.8.........4.27.6...3.1..7.4.72..4..6...4.1...3',
 '......9.7...42.18....7.5.261..9.4....5.....4....5.7..992.1.8....34.59...5.7......',
 '.3..5..4...8.1.5..46.....12.7.5.2.8....6.3....4.1.9.3.25.....98..1.2.6...8..6..2.',
 '.2.81.74.7....31...9...28.5..9.4..874..2.8..316..3.2..3.27...6...56....8.76.51.9.',
 '1..92....524.1...........7..5...81.2.........4.27...9..6...........3.945....71..6',
 '.43.8.25.6.............1.949....4.7....6.8....1.2....382.5.............5.34.9.71.',
 '48...69.2..2..8..19..37..6.84..1.2....37.41....1.6..49.2..85..77..9..6..6.92...18',
 '...9....2.5.1234...3....16.9.8.......7.....9.......2.5.91....5...7439.2.4....7...',
 '..19....39..7..16..3...5..7.5......9..43.26..2......7.6..1...3..42..7..65....68..',
 '...1254....84.....42.8......3.....95.6.9.2.1.51.....6......3.49.....72....1298...',
 '.6234.75.1....56..57.....4.....948..4.......6..583.....3.....91..64....7.59.8326.',
 '3..........5..9...2..5.4....2....7..16.....587.431.6.....89.1......67.8......5437',
 '63..........5....8..5674.......2......34.1.2.......345.....7..4.8.3..9.29471...8.',
 '....2..4...8.35.......7.6.2.31.4697.2...........5.12.3.49...73........1.8....4...',
 '361.259...8.96..1.4......57..8...471...6.3...259...8..74......5.2..18.6...547.329',
 '.5.8.7.2.6...1..9.7.254...6.7..2.3.15.4...9.81.3.8..7.9...762.5.6..9...3.8.1.3.4.',
 '.8...5........3457....7.8.9.6.4..9.3..7.1.5..4.8..7.2.9.1.2....8423........1...8.',
 '..35.29......4....1.6...3.59..251..8.7.4.8.3.8..763..13.8...1.4....2......51.48..',
 '...........98.51...519.742.29.4.1.65.........14.5.8.93.267.958...51.36...........',
 '.2..3..9....9.7...9..2.8..5..48.65..6.7...2.8..31.29..8..6.5..7...3.9....3..2..5.',
 '..5.....6.7...9.2....5..1.78.415.......8.3.......928.59.7..6....3.4...1.2.....6..',
 '.4.....5...19436....9...3..6...5...21.3...5.68...2...7..5...2....24367...3.....4.',
 '..4..........3...239.7...8.4....9..12.98.13.76..2....8.1...8.539...4..........8..',
 '36..2..89...361............8.3...6.24..6.3..76.7...1.8............418...97..3..14',
 '5..4...6...9...8..64..2.........1..82.8...5.17..5.........9..84..3...6...6...3..2',
 '..72564..4.......5.1..3..6....5.8.....8.6.2.....1.7....3..7..9.2.......4..63127..',
 '..........79.5.18.8.......7..73.68..45.7.8.96..35.27..7.......5.16.3.42..........',
 '.3.....8...9...5....75.92..7..1.5..8.2..9..3.9..4.2..1..42.71....2...8...7.....9.',
 '2..17.6.3.5....1.......6.79....4.7.....8.1.....9.5....31.4.......5....6.9.6.37..2',
 '.......8.8..7.1.4..4..2..3.374...9......3......5...321.1..6..5..5.8.2..6.8.......',
 '.......85...21...996..8.1..5..8...16.........89...6..7..9.7..523...54...48.......',
 '6.8.7.5.2.5.6.8.7...2...3..5...9...6.4.3.2.5.8...5...3..5...2...1.7.4.9.4.9.6.7.1',
 '.5..1..4.1.7...6.2...9.5...2.8.3.5.1.4..7..2.9.1.8.4.6...4.1...3.4...7.9.2..6..1.',
 '.53...79...97534..1.......2.9..8..1....9.7....8..3..7.5.......3..76412...61...94.',
 '..6.8.3...49.7.25....4.5...6..317..4..7...8..1..826..9...7.2....75.4.19...3.9.6..',
 '..5.8.7..7..2.4..532.....84.6.1.5.4...8...5...7.8.3.1.45.....916..5.8..7..3.1.6..',
 '...9..8..128..64...7.8...6.8..43...75.......96...79..8.9...4.1...36..284..1..7...',
 '....8....27.....54.95...81...98.64...2.4.3.6...69.51...17...62.46.....38....9....',
 '...6.2...4...5...1.85.1.62..382.671...........194.735..26.4.53.9...2...7...8.9...',
 '...9....2.5.1234...3....16.9.8.......7.....9.......2.5.91....5...7439.2.4....7...',
 '38..........4..785..9.2.3...6..9....8..3.2..9....4..7...1.7.5..495..6..........92',
 '...158.....2.6.8...3.....4..27.3.51...........46.8.79..5.....8...4.7.1.....325...',
 '.1.5..2..9....1.....2..8.3.5...3...7..8...5..6...8...4.4.1..7.....7....6..3..4.5.',
 '.8.....4....469...4.......7..59.46...7.6.8.3...85.21..9.......5...781....6.....1.',
 '9.42....7.1..........7.65.....8...9..2.9.4.6..4...2.....16.7..........3.3....57.2',
 '...7..8....6....31.4...2....24.7.....1..3..8.....6.29....8...7.86....5....2..6...',
 '..1..7.9.59..8...1.3.....8......58...5..6..2...41......8.....3.1...2..79.2.7..4..',
 '.....3.17.15..9..8.6.......1....7.....9...2.....5....4.......2.5..6..34.34.2.....',
 '3..2........1.7...7.6.3.5...7...9.8.9...2...4.1.8...5...9.4.3.1...7.2........8..6']

# hard = ["4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......",
#         "52...6.........7.13...........4..8..6......5...........418.........3..2...87....."]
# all 95 hard problems
hard = ['4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......',
 '52...6.........7.13...........4..8..6......5...........418.........3..2...87.....',
 '6.....8.3.4.7.................5.4.7.3..2.....1.6.......2.....5.....8.6......1....',
 '48.3............71.2.......7.5....6....2..8.............1.76...3.....4......5....',
 '....14....3....2...7..........9...3.6.1.............8.2.....1.4....5.6.....7.8...',
 '......52..8.4......3...9...5.1...6..2..7........3.....6...1..........7.4.......3.',
 '6.2.5.........3.4..........43...8....1....2........7..5..27...........81...6.....',
 '.524.........7.1..............8.2...3.....6...9.5.....1.6.3...........897........',
 '6.2.5.........4.3..........43...8....1....2........7..5..27...........81...6.....',
 '.923.........8.1...........1.7.4...........658.........6.5.2...4.....7.....9.....',
 '6..3.2....5.....1..........7.26............543.........8.15........4.2........7..',
 '.6.5.1.9.1...9..539....7....4.8...7.......5.8.817.5.3.....5.2............76..8...',
 '..5...987.4..5...1..7......2...48....9.1.....6..2.....3..6..2.......9.7.......5..',
 '3.6.7...........518.........1.4.5...7.....6.....2......2.....4.....8.3.....5.....',
 '1.....3.8.7.4..............2.3.1...........958.........5.6...7.....8.2...4.......',
 '6..3.2....4.....1..........7.26............543.........8.15........4.2........7..',
 '....3..9....2....1.5.9..............1.2.8.4.6.8.5...2..75......4.1..6..3.....4.6.',
 '45.....3....8.1....9...........5..9.2..7.....8.........1..4..........7.2...6..8..',
 '.237....68...6.59.9.....7......4.97.3.7.96..2.........5..47.........2....8.......',
 '..84...3....3.....9....157479...8........7..514.....2...9.6...2.5....4......9..56',
 '.98.1....2......6.............3.2.5..84.........6.........4.8.93..5...........1..',
 '..247..58..............1.4.....2...9528.9.4....9...1.........3.3....75..685..2...',
 '4.....8.5.3..........7......2.....6.....5.4......1.......6.3.7.5..2.....1.9......',
 '.2.3......63.....58.......15....9.3....7........1....8.879..26......6.7...6..7..4',
 '1.....7.9.4...72..8.........7..1..6.3.......5.6..4..2.........8..53...7.7.2....46',
 '4.....3.....8.2......7........1...8734.......6........5...6........1.4...82......',
 '.......71.2.8........4.3...7...6..5....2..3..9........6...7.....8....4......5....',
 '6..3.2....4.....8..........7.26............543.........8.15........8.2........7..',
 '.47.8...1............6..7..6....357......5....1..6....28..4.....9.1...4.....2.69.',
 '......8.17..2........5.6......7...5..1....3...8.......5......2..4..8....6...3....',
 '38.6.......9.......2..3.51......5....3..1..6....4......17.5..8.......9.......7.32',
 '...5...........5.697.....2...48.2...25.1...3..8..3.........4.7..13.5..9..2...31..',
 '.2.......3.5.62..9.68...3...5..........64.8.2..47..9....3.....1.....6...17.43....',
 '.8..4....3......1........2...5...4.69..1..8..2...........3.9....6....5.....2.....',
 '..8.9.1...6.5...2......6....3.1.7.5.........9..4...3...5....2...7...3.8.2..7....4',
 '4.....5.8.3..........7......2.....6.....5.8......1.......6.3.7.5..2.....1.8......',
 '1.....3.8.6.4..............2.3.1...........958.........5.6...7.....8.2...4.......',
 '1....6.8..64..........4...7....9.6...7.4..5..5...7.1...5....32.3....8...4........',
 '249.6...3.3....2..8.......5.....6......2......1..4.82..9.5..7....4.....1.7...3...',
 '...8....9.873...4.6..7.......85..97...........43..75.......3....3...145.4....2..1',
 '...5.1....9....8...6.......4.1..........7..9........3.8.....1.5...2..4.....36....',
 '......8.16..2........7.5......6...2..1....3...8.......2......7..3..8....5...4....',
 '.476...5.8.3.....2.....9......8.5..6...1.....6.24......78...51...6....4..9...4..7',
 '.....7.95.....1...86..2.....2..73..85......6...3..49..3.5...41724................',
 '.4.5.....8...9..3..76.2.....146..........9..7.....36....1..4.5..6......3..71..2..',
 '.834.........7..5...........4.1.8..........27...3.....2.6.5....5.....8........1..',
 '..9.....3.....9...7.....5.6..65..4.....3......28......3..75.6..6...........12.3.8',
 '.26.39......6....19.....7.......4..9.5....2....85.....3..2..9..4....762.........4',
 '2.3.8....8..7...........1...6.5.7...4......3....1............82.5....6...1.......',
 '6..3.2....1.....5..........7.26............843.........8.15........8.2........7..',
 '1.....9...64..1.7..7..4.......3.....3.89..5....7....2.....6.7.9.....4.1....129.3.',
 '.........9......84.623...5....6...453...1...6...9...7....1.....4.5..2....3.8....9',
 '.2....5938..5..46.94..6...8..2.3.....6..8.73.7..2.........4.38..7....6..........5',
 '9.4..5...25.6..1..31......8.7...9...4..26......147....7.......2...3..8.6.4.....9.',
 '...52.....9...3..4......7...1.....4..8..453..6...1...87.2........8....32.4..8..1.',
 '53..2.9...24.3..5...9..........1.827...7.........981.............64....91.2.5.43.',
 '1....786...7..8.1.8..2....9........24...1......9..5...6.8..........5.9.......93.4',
 '....5...11......7..6.....8......4.....9.1.3.....596.2..8..62..7..7......3.5.7.2..',
 '.47.2....8....1....3....9.2.....5...6..81..5.....4.....7....3.4...9...1.4..27.8..',
 '......94.....9...53....5.7..8.4..1..463...........7.8.8..7.....7......28.5.26....',
 '.2......6....41.....78....1......7....37.....6..412....1..74..5..8.5..7......39..',
 '1.....3.8.6.4..............2.3.1...........758.........7.5...6.....8.2...4.......',
 '2....1.9..1..3.7..9..8...2.......85..6.4.........7...3.2.3...6....5.....1.9...2.5',
 '..7..8.....6.2.3...3......9.1..5..6.....1.....7.9....2........4.83..4...26....51.',
 '...36....85.......9.4..8........68.........17..9..45...1.5...6.4....9..2.....3...',
 '34.6.......7.......2..8.57......5....7..1..2....4......36.2..1.......9.......7.82',
 '......4.18..2........6.7......8...6..4....3...1.......6......2..5..1....7...3....',
 '.4..5..67...1...4....2.....1..8..3........2...6...........4..5.3.....8..2........',
 '.......4...2..4..1.7..5..9...3..7....4..6....6..1..8...2....1..85.9...6.....8...3',
 '8..7....4.5....6............3.97...8....43..5....2.9....6......2...6...7.71..83.2',
 '.8...4.5....7..3............1..85...6.....2......4....3.26............417........',
 '....7..8...6...5...2...3.61.1...7..2..8..534.2..9.......2......58...6.3.4...1....',
 '......8.16..2........7.5......6...2..1....3...8.......2......7..4..8....5...3....',
 '.2..........6....3.74.8.........3..2.8..4..1.6..5.........1.78.5....9..........4.',
 '.52..68.......7.2.......6....48..9..2..41......1.....8..61..38.....9...63..6..1.9',
 '....1.78.5....9..........4..2..........6....3.74.8.........3..2.8..4..1.6..5.....',
 '1.......3.6.3..7...7...5..121.7...9...7........8.1..2....8.64....9.2..6....4.....',
 '4...7.1....19.46.5.....1......7....2..2.3....847..6....14...8.6.2....3..6...9....',
 '......8.17..2........5.6......7...5..1....3...8.......5......2..3..8....6...4....',
 '963......1....8......2.5....4.8......1....7......3..257......3...9.2.4.7......9..',
 '15.3......7..4.2....4.72.....8.........9..1.8.1..8.79......38...........6....7423',
 '..........5724...98....947...9..3...5..9..12...3.1.9...6....25....56.....7......6',
 '....75....1..2.....4...3...5.....3.2...8...1.......6.....1..48.2........7........',
 '6.....7.3.4.8.................5.4.8.7..2.....1.3.......2.....5.....7.9......1....',
 '....6...4..6.3....1..4..5.77.....8.5...8.....6.8....9...2.9....4....32....97..1..',
 '.32.....58..3.....9.428...1...4...39...6...5.....1.....2...67.8.....4....95....6.',
 '...5.3.......6.7..5.8....1636..2.......4.1.......3...567....2.8..4.7.......2..5..',
 '.5.3.7.4.1.........3.......5.8.3.61....8..5.9.6..1........4...6...6927....2...9..',
 '..5..8..18......9.......78....4.....64....9......53..2.6.........138..5....9.714.',
 '..........72.6.1....51...82.8...13..4.........37.9..1.....238..5.4..9.........79.',
 '...658.....4......12............96.7...3..5....2.8...3..19..8..3.6.....4....473..',
 '.2.3.......6..8.9.83.5........2...8.7.9..5........6..4.......1...1...4.22..7..8.9',
 '.5..9....1.....6.....3.8.....8.4...9514.......3....2..........4.8...6..77..15..6.',
 '.....2.......7...17..3...9.8..7......2.89.6...13..6....9..5.824.....891..........',
 '3...8.......7....51..............36...2..4....7...........6.13..452...........8..']

for problem in easy:
    print("====Problem====")
    g = Grid(problem)
    # Display the original problem
    g.display()
    s = Solver(g)
    if s.solve():
        print("====Solution===")
        # Display the solution
        # Feel free to call other functions to display
        s.display(s.solution)
    else:
        print("==No solution==")
        break

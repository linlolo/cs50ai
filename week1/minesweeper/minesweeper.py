import itertools
import random


class KnowledgeCountError(Exception):
    pass


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return set(self.cells)
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return set(self.cells)
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def in_range(self, r, c):
        """
        checks if cell is in range of the board
        """
        return 0 <= r < self.height and 0 <= c < self.width

    def neighbors(self, r, c):
        """
        returns all neighbors of a given cell as a set
        """
        neigh = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                row = r+i
                col = c+j
                if self.in_range(row, col) and (row, col) not in self.moves_made:
                    neigh.add((row, col))
        return neigh

    def reduce_set(self, sentence1, sentence2):
        """
        reduces sentence2 by sentence1,
        where sentence2 is a subset of sentence1
        """
        sentence2.cells = sentence2.cells - sentence1.cells
        sentence2.count = sentence2.count - sentence1.count

    def find_set_diff(self, sentence1, sentence2):
        """
        checks if two knowledge sentences are subsets of the other
        and reduce the cells and count
        """
        if sentence1.cells < sentence2.cells:
            self.reduce_set(sentence1, sentence2)
            return True
        elif sentence2.cells < sentence1.cells:
            self.reduce_set(sentence2, sentence1)
            return True
        return False

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def update_mine_safe(self):
        """

        """
        # returns boolean if an update has been made
        update = False
        # check all safes
        for i, sentence in enumerate(self.knowledge):
            new_safes = sentence.known_safes()
            if new_safes:
                update = True
                for safe in new_safes:
                    self.mark_safe(safe)
        # check all mines
        for i, sentence in enumerate(self.knowledge):
            new_mines = sentence.known_mines()
            if new_mines:
                update = True
                for mine in new_mines:
                    self.mark_mine(mine)
                self.knowledge.pop(i)

        for i in range(len(self.knowledge)):
            if not self.knowledge[i].cells:
                if self.knowledge[i].count != 0:
                    raise KnowledgeCountError
                self.knowledge.pop(i)

        return update
    
    def infer_knowledge(self):
        updated = False
        for i in range(len(self.knowledge)):
            sentence1 = self.knowledge[i]
            for j in range(i+1, len(self.knowledge)):
                if self.find_set_diff(sentence1, self.knowledge[j]):
                    updated = True
            for cell in sentence1.cells:
                if cell in self.mines:
                    sentence1.mark_mine(cell)
                    updated = True
                elif cell in self.safes:
                    sentence1.mark_safe(cell)
                    updated = True
        return updated

    def knowledge_loop(self):
        return self.update_mine_safe() or self.infer_knowledge()
    
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        i, j = cell
        # mark move as move made and safe
        self.moves_made.add((i, j))
        self.mark_safe((i, j))
        new_sentence = Sentence(self.neighbors(i, j), count)
        for cell in set(new_sentence.cells):
            if cell in self.mines:
                new_sentence.mark_mine(cell)
            elif cell in self.safes:
                new_sentence.mark_safe(cell)
        if new_sentence.cells:
            self.knowledge.append(new_sentence)

        while self.knowledge_loop():
            # keep iterating if there is new knowledge gained
            pass

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = list(self.safes - self.moves_made)
        if safe_moves:
            return safe_moves[0]
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        available_moves = []    # list of all available random moves
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    available_moves.append((i, j))

        if available_moves:
            return available_moves[random.randrange(len(available_moves))]
        else:
            return None

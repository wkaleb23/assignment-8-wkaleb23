import random

import png
from PIL import Image, ImageDraw

class Grid:
    def __init__(self, num_rows, num_cols):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.rows = None

        self.prepare_grid()
        self.configure_cells()

    ## Populate the rows with cells
    def prepare_grid(self):
        """Set up 2D array of Cells"""
        #  Create all the rows, populating them by creating cells
        self.rows = [[Cell(row, col) for col in range(self.num_cols)] for row in range(self.num_rows)]


    ## If either which_row or which_col is invalid (negative or greater than the number of
    ##   rows or cols), return None.
    ## Else, return the cell at the given location
    def get_cell(self, which_row, which_col):
        if which_row < 0 or which_row >= self.num_rows:
            return None
        if which_col < 0 or which_col >= self.num_cols:
            return None
        return self.rows[which_row][which_col]


    def configure_cells(self):
        # iterate through all the cells, telling each cell what it's neighbors are (e.g. what Cell.north, etc are)
        # Hint: The north neighbor of cell is the one at row cell.row - 1 and column cell.col

        # iterate through all the cells
        for row in range(len(self.rows)):
            for col in range(len(self.rows[0])):
                # set the north neighbor
                self.rows[row][col].set_neighbor(Cell.NORTH, self.get_cell(row - 1, col))
                # set the south neighbor
                self.rows[row][col].set_neighbor(Cell.SOUTH, self.get_cell(row + 1, col))
                # set the east neighbor
                self.rows[row][col].set_neighbor(Cell.EAST, self.get_cell(row, col + 1))
                # set the west neighbor
                self.rows[row][col].set_neighbor(Cell.WEST, self.get_cell(row, col - 1))
        
    ## This may not be used; depends on what Maze algorithms we end up implementing!
    """Return a random cell"""
    def random_cell(self):
        random_row = random.randint(0, self.num_rows - 1)
        random_col = random.randint(0, self.num_cols - 1)
        return self.rows[random_row][random_col]


    """Return how many cells are in this grid"""
    def size(self):
        return self.num_rows * self.num_cols

    """Returns a flattened list of all the cells """
    def all_cells(self):
        return [cell for row in self.rows for cell in row]

    def __iter__(self):
        return GridIterator(self)

    """Prints the grid. See the README for some guidance. """
    def print(self):
        # Print the top boundary
        print('+' + '---+' * len(self.rows[0]))

        for row in self.rows:
            # Print the west boundary
            print('|', end='')
            # print the east walls of each cell, if the cell is linked to the cell to the east, it's a passage, don't print the pipe
            for cell in row:
                if cell.is_linked(cell.get_neighbor(Cell.EAST)):
                    print('    ', end='')
                else:
                    print('   |', end='')
            print()
            # Print the plus ('+'), for the West edge of the maze
            print('+', end='')
            # print the south walls of each cell, if the cell is linked to the cell to the south, it's a passage, don't print the '---'
            for cell in row:
                if cell.is_linked(cell.get_neighbor(Cell.SOUTH)):
                    print('   +', end='')
                else:
                    print('---+', end='')
            print()


    def export_image(self, filename = "amaze.png", path = None):
        tile_ht = 50
        tile_wid = 50
        maze_image = Image.new("RGBA", (tile_wid * self.num_cols, tile_ht * self.num_rows), (255, 255, 255,255))
        for which_row, row in enumerate(self.rows):
            for which_col, cell in enumerate(row):
                tile = cell.get_image()
                maze_image.paste(tile, (tile_wid * which_col, tile_ht*which_row))


        if path and len(path) > 1:
            print("Printing the path")
            print(path)
            print("Done printing the path")
            draw = ImageDraw.Draw(maze_image)
            cell1 = path[0]
            for cell2 in path[1:]:
                draw.line((cell1.col * 50 + 15, cell1.row * 50 + 35, cell2.col*50+15, cell2.row *50+ 35), fill=(255, 50, 50, 200), width=10)
                cell1 = cell2

        try:
            maze_image.save("images/" + filename)
        except OSError:
            print("cannot convert", "someatjelsakjr")


class GridIterator:
    def __init__(self, grid):
        self.row_iterator = grid.rows.__iter__()
        self.col_iterator = self.row_iterator.__next__().__iter__()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.col_iterator.__next__()
        except StopIteration:
            ## No more cells in this row; go to the next one
            try:
                self.col_iterator = self.row_iterator.__next__().__iter__()
                return self.__next__() ## Recursive call so we can move on from an empty row
            except StopIteration:
                ## No more rows left to visit
                raise StopIteration

class Cell:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    ## Used for the images
    border_color = (100, 100, 100)
    background_color = (200, 200, 200)
    border_width = 6

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.neighbor_cells = {} ## Use a Python dict to make it easy
        self.links = []   # Which cells are linked to this cell
        self.content = " "
        self.distance = 0 ## Attribute to hold the distance from a source node to this node

    """Set the specified neighbor of this cell. """
    ## which_neighbor must be one of Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST
    ## If which_neighbor is not one of these, raise a NotImplementedError
    ## If no cell is provided, do nothing.
    def set_neighbor(self, which_neighbor, cell):
        if which_neighbor not in [Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST]:
            raise NotImplementedError
        if cell is not None:
            self.neighbor_cells[which_neighbor] = cell
        

    ## Gets the specified neighbor of this cell
    ## which_neighbor must be one of Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST
    ## If which_neighbor is not one of these, raise a NotImplementedError
    ## Returns None if the key is valid but no assigned neighbor
    def get_neighbor(self, which_neighbor):
        if which_neighbor not in [Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST]:
            raise NotImplementedError
        return self.neighbor_cells.get(which_neighbor, None)

    ## Creates an edge between this cell and the provided cell.
    ## If bidirectional, create an edge between the other cell and this cell
    ## There is an edge from this cell to another cell if the other cell is in this cell's links list.
    def link(self, cell, bidirectional = True):
        if cell is not None:
            self.links.append(cell)
            if bidirectional:
                cell.link(self, False)

    ## Removes an edge between this cell and the specified cell.
    ## If bidirectional, remove the edge between the other cell and this cell
    ## There is an edge from this cell to another cell if the other cell is in this cell's links list.
    def unlink(self, cell, bidirectional = True):
        if cell in self.links:
            self.links.remove(cell)
            if bidirectional:
                cell.unlink(self, False)

    """Returns Treu if the other cell is linked to this one"""
    def is_linked(self, cell):
        return cell in self.links

    """Returns all the neighbors of this cell as a list"""
    def neighbors(self):
        return list(self.neighbor_cells.values())

    ### Returns the linked neighboring cell that has the shortest distance
    def get_closest_cell(self):
        if not self.links:
            return None
        return min(self.links, key=lambda cell: cell.distance)

    ## Feel free to tweak this to print something different if you'd like
    def print(self):
        print(f"Cell (x: {self.row}, y:{self.col})")

    def __str__(self):
        return f"Cell (x: {self.row}, y:{self.col}, dist: {self.distance}, content: {self.content})"

    def __repr__(self):
        return f"Cell (x: {self.row}, y:{self.col}, dist: {self.distance}, content: {self.content})"

    def get_image(self):
        tile_ht = 50
        tile_wid = 50
        tile = Image.new("RGBA", (tile_wid, tile_ht), self.background_color)
        with tile as im:
            draw = ImageDraw.Draw(im)
            if not self.get_neighbor(Cell.NORTH):
                draw.line((0, 0, tile_wid, 0), fill=self.border_color, width=self.border_width, joint="curve")
            if not self.get_neighbor(Cell.WEST):
                draw.line((0, 0, 0,im.size[1]), fill=self.border_color, width = self.border_width)
            if not self.get_neighbor(Cell.EAST):
                draw.line((im.size[1], 0, im.size[1],im.size[1]), fill=self.border_color, width = self.border_width,joint="curve")
            if not self.get_neighbor(Cell.SOUTH):
                draw.line((0, im.size[1], im.size[0],im.size[1]), fill=self.border_color, width = self.border_width,joint="curve")

            ## Draw the boundaries
            draw.line((0, 0, 0, im.size[1]), fill=self.border_color, width=self.border_width)
            draw.line((0, im.size[1], im.size[0], im.size[1]), fill=self.border_color, width=self.border_width)

            ## Erase them if we're linked
            half_border = self.border_width / 2
            for link in self.links:
                if link == self.get_neighbor(Cell.WEST):
                    draw.line((0, 0+half_border, 0, im.size[1]-half_border), fill=self.background_color, width=self.border_width)
                if link == self.get_neighbor(Cell.SOUTH):
                    draw.line((0+half_border, im.size[1], im.size[0]-half_border,im.size[1]), fill=self.background_color, width = self.border_width)

            ## Draw the content
            draw.text((im.size[0]/2, im.size[1]/2), str(self.content), fill="black", anchor="mm")

        ## This chunk of code will save an image of just this cell
        ## Feel free to uncomment to help with debugging if needed
        # try:
        #     tile.save(f"images/cell{self.row}-{self.col}.png")
        # except OSError:
        #     print("cannot convert", "Couldn't save the file")
        return tile

class BinaryTreeMazeMaker():

    def __init__(self, grid):
        ## For each cell in the grid
        for index, cell in enumerate(grid):
            ## Set the neighbors to an empty list
            neighbors = []

            ## If the current cell has a neighbor to the south or east, add it to the neighbors list
            if cell.get_neighbor(Cell.SOUTH):
                neighbors.append(cell.get_neighbor(Cell.SOUTH))
            if cell.get_neighbor(Cell.EAST):
                neighbors.append(cell.get_neighbor(Cell.EAST))

            if len(neighbors) > 0:
                ## Choose a random neighbor
                neighbor = random.choice(neighbors)
                ## Link them together
                cell.link(neighbor)

class SidewinderMazeMaker:
    
    def __init__(self, grid, seed = None):
        self.grid = grid
        self.random = random.Random(seed)
        self.make_maze()

    def flip_coin(self):
        # helper function to "flip a coin"
        return self.random.randint(0, 1)
    
    def remove_eastern_wall(self, cell):
        # helper function to remove the eastern wall of a cell
        if cell.get_neighbor(Cell.EAST):
            cell.link(cell.get_neighbor(Cell.EAST))
            
    def remove_southern_wall(self, cell):
        # helper function to remove the southern wall of a cell
        if cell.get_neighbor(Cell.SOUTH):
            cell.link(cell.get_neighbor(Cell.SOUTH))
            
    def make_maze(self):
        # iterate through the grid
        # "Flip a coin": Get a random number between 0 and 1
        # If "tails" (e.g. the random number is 0)
        # Erase the east wall
        # Move to the eastern neighbor ("go through the corridor")
        # If "heads" (e.g. the random number is 1)
        # Choose one of the cells that we've just linked together, and delete the south wall.
        # Move to the next eastern neighbor.
        # If you're at a cell that has no eastern neighbor, just delete the south wall.
        # Go to the start of the next row, and repeat the process.
        # If you're in the last row, instead of choosing between removing the east or south wall, just remove the east wall.

        for row in self.grid.rows:
            run = []
            # if it's teh last row, just remove the eastern wall
            if row == self.grid.rows[-1]:
                for cell in row:
                    self.remove_eastern_wall(cell)
            else:
                for cell in row:
                    run.append(cell)
                    # if you're at a cell that has no eastern neighbor, just delete the south wall
                    if cell.get_neighbor(Cell.EAST) is None:
                        # remove the southern wall
                        self.remove_southern_wall(cell)
                        
                    else:    
                        flip = self.flip_coin()
                        if flip == 0:
                            # erase the eastern wall (unless we're at the last cell in the row)
                            if cell.get_neighbor(Cell.EAST):
                                self.remove_eastern_wall(cell)
                            else:
                                # if we're at the last cell in the row, remove the southern wall
                                self.remove_southern_wall(cell)
                        else:
                            # choose a random cell from the run and remove the southern wall
                            random_cell = self.random.choice(run)
                            self.remove_southern_wall(random_cell)
                            run = []

        # After creating the maze, check for any unlinked cells and link them
        for row in self.grid.rows:
            for cell in row:
                if not cell.links:
                    # If the cell has no links, randomly link it to a neighbor
                    neighbors = [neighbor for neighbor in cell.neighbor_cells.values() if neighbor]
                    if neighbors:
                        random_neighbor = self.random.choice(neighbors)
                        cell.link(random_neighbor)
                    

class DjikstraSolver():

    def __init__(self, grid):
        self.grid = grid

    def solve(self):
        ## Initialize source distances
        ## Set the distance to the source node to be 0
        ## Put all the nodes in a queue
        ## While there are more nodes in the queue

            ## Find the node with the smallest distance
            ## Add that node to the set S (nodes we know the distance to)
            ## For all the neighbors of that node:
            ## Relax (u, v, w)

        ## Return the recovered path
        self.initialize()
        start = self.grid.get_cell(0, 0)
        start.distance = 0
        unvisited = list(self.grid)

        while unvisited:
            current = min(unvisited, key=lambda cell: cell.distance)
            unvisited.remove(current)

            for neighbor in current.links:
                # Relax (u, v, w)
                self.relax(neighbor)

        return self.recover_path()

    ## Set the distance for all the cells to be "Infinity" (or, 10000 for this assignment)
    def initialize(self):
        for cell in self.grid:
            cell.distance = 10000  # Set initial distance to a large number

    ## The weight function to determine the weight of the edge between 2 nodes
    def weight(self, cell1: Cell, cell2: Cell):
        ## Return the weight of the edge between cell1 and cell2
        ## 1 if there is a passage between the two,
        ## [] if there is a wall between the two: the distance to go through the whole ....
        ## Infinity (10000) if the two nodes are not connected
        if cell1.is_linked(cell2):
            return 1
        else:
            return 10000  # Return a large number if cells are not linked

    ## Updates the weights; see Relax() in the Djikstra Algorithm slides
    ## If cell is None, do nothing/return
    def relax(self, cell1: Cell):
        ## For each neighbor
            ## New distance between is the distance to cell1 plus the distance between cell1 and cell2
            ## if the new distance is less than the distance to cell2:
                ## Set the distance to cell2 to be newDistance
        neighbors = cell1.neighbors()      
        for neighbor in neighbors:
            tentative_distance = cell1.distance + self.weight(cell1, neighbor)
            
            if tentative_distance < neighbor.distance:
                neighbor.distance = tentative_distance

    ## Find the actual path from the source to the target
    ##   utilizing the distances calculated by Djikstra's.
    ## Return a list with the series of nodes that make the shortest path from the source to the target.
    def recover_path(self):
        ## There are many ways to do this; Here's an outline for one approach.
        ##   Feel free to ignore and come up with your own if you'd like!
        ## Get the source node
        ## Get the target/last node
        ## Put the target in the output list
        ## While we're not yet at the source, find the neighboring cell with the
        ##   shortest distance assigned to it
        ## Add it to the output list
        ## If we ever can't find a neighbor (shouldn't happen), return an empty list
        end = self.grid.get_cell(len(self.grid.rows) - 1, len(self.grid.rows[0]) - 1)
        path = [end]
        current = end

        while current.distance > 0:
            for neighbor in current.links:
                if neighbor.distance < current.distance:
                    path.append(neighbor)
                    current = neighbor
                    break
            else:
                return []

        path.reverse()
        return path

def main():
    # create some nice mazes and save them to images
    # create a grid
    grid = Grid(12, 12)
    # create a maze
    BinaryTreeMazeMaker(grid)
    # export the maze to an image
    grid.print()
    grid.export_image("binary_tree_maze.png")
    
    # create a grid
    grid = Grid(12, 12)
    # create a maze
    SidewinderMazeMaker(grid)
    # export the maze to an image
    grid.print()
    grid.export_image("sidewinder_maze.png")
    
    # Now let's solve a maze
    # create a grid
    grid = Grid(15, 15)
    # create a maze
    BinaryTreeMazeMaker(grid)
    # solve the maze
    solver = DjikstraSolver(grid)
    path = solver.solve()
    # export the maze to an image
    grid.print()
    grid.export_image("solved_maze.png", path)
    
    # create a grid
    grid = Grid(15, 15)
    # create a maze
    SidewinderMazeMaker(grid)
    # solve the maze
    solver = DjikstraSolver(grid)
    path = solver.solve()
    # export the maze to an image
    grid.print()
    grid.export_image("solved_maze2.png", path)
    
if __name__ == "__main__":
    main()
    
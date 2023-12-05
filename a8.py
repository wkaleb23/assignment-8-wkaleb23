
import random

import png
from PIL import Image, ImageDraw

class Grid:
    def __init__(self, num_rows, num_cols):
        self.rows = None
        self.num_rows = num_rows
        self.num_cols = num_cols

        self.prepare_grid()
        self.configure_cells()

    ## Populate the rows with cells
    def prepare_grid(self):
        """Set up 2D array of Cells"""
        pass


    ## If either which_row or which_col is invalid (negative or greater than the number of
    ##   rows or cols), return None.
    ## Else, return the cell at the given location
    def get_cell(self, which_row, which_col):
        pass

    def configure_cells(self):
        """Tell all the cells who their neighbors are"""
        pass

    ## This may not be used; depends on what Maze algorithms we end up implementing!
    """Return a random cell"""
    def random_cell(self):
        pass

    """Return how many cells are in this grid"""
    def size(self):
        pass

    """Returns a flattened list of all the cells """
    def all_cells(self):
        return [cell for row in self.rows for cell in row]

    def __iter__(self):
        return GridIterator(self)

    """Prints the grid. See the README for some guidance. """
    def print(self):
        pass


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
        pass

    ## Gets the specified neighbor of this cell
    ## which_neighbor must be one of Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST
    ## If which_neighbor is not one of these, raise a NotImplementedError
    ## Returns None if the key is valid but no assigned neighbor
    def get_neighbor(self, which_neighbor):
        pass

    ## Creates an edge between this cell and the provided cell.
    ## If bidirectional, create an edge between the other cell and this cell
    ## There is an edge from this cell to another cell if the other cell is in this cell's links list.
    def link(self, cell, bidirectional = True):
        pass

    ## Removes an edge between this cell and the specified cell.
    ## If bidirectional, remove the edge between the other cell and this cell
    ## There is an edge from this cell to another cell if the other cell is in this cell's links list.
    def unlink(self, cell, bidirectional = True):
        pass

    """Returns Treu if the other cell is linked to this one"""
    def is_linked(self, cell):
        pass

    """Returns all the neighbors of this cell as a list"""
    def neighbors(self):
        pass

    ### Returns the linked neighboring cell that has the shortest distance
    def get_closest_cell(self):
        pass

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


class SidewinderMazeMaker():

    def __init__(self, grid):
        ## See the README for a description of the Sidewinder Maze Maker algorithm
        pass



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
        pass

    ## Set the distance for all the cells to be "Infinity" (or, 10000 for this assignment)
    def initialize(self):
        pass

    ## The weight function to determine the weight of the edge between 2 nodes
    def weight(self, cell1: Cell, cell2: Cell):
        ## Return the weight of the edge between cell1 and cell2
        ## 1 if there is a passage between the two,
        ## [] if there is a wall between the two: the distance to go through the whole ....
        ## Infinity (10000) if the two nodes are not connected
        pass

    ## Updates the weights; see Relax() in the Djikstra Algorithm slides
    ## If cell is None, do nothing/return
    def relax(self, cell1: Cell):
        ## For each neighbor
            ## New distance between is the distance to cell1 plus the distance between cell1 and cell2
            ## if the new distance is less than the distance to cell2:
                ## Set the distance to cell2 to be newDistance
        pass

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
        ## Once we get to the source, reverse the list and return
        pass



from a8 import Grid, Cell, BinaryTreeMazeMaker, SidewinderMazeMaker, DjikstraSolver
import pytest

class TestCell:
    def test_cell_core(self):
        cell = Cell(5, 6)
        assert cell.row == 5
        assert cell.col == 6
        assert len(cell.neighbor_cells) == 0
        assert len(cell.links) == 0
        assert cell.content == " "
        assert cell.distance == 0

    def test_cell_link_bidirectional(self):
        cell1 = Cell(5, 6)
        cell2 = Cell(2, 4)

        cell1.link(cell2)

        assert len(cell1.links) == 1
        assert len(cell2.links) == 1

        assert cell1 in cell2.links
        assert cell2 in cell1.links

    def test_cell_link_unidirectional(self):
        cell1 = Cell(5, 6)
        cell2 = Cell(2, 4)

        cell1.link(cell2, bidirectional = False)

        assert len(cell1.links) == 1
        assert len(cell2.links) == 0

        assert cell1 not in cell2.links
        assert cell2 in cell1.links

    def test_cell_unlink_bidirectional(self):
        cell1 = Cell(5, 6)
        cell2 = Cell(2, 4)
        cell1.link(cell2)

        cell1.unlink(cell2)

        assert len(cell1.links) == 0
        assert len(cell2.links) == 0

        assert cell1 not in cell2.links
        assert cell2 not in cell1.links

    def test_cell_unlink_unidirectional(self):
        cell1 = Cell(5, 6)
        cell2 = Cell(2, 4)
        cell1.link(cell2) ## Link Bidirection

        cell1.unlink(cell2, False) ## Unlink Unidirection

        assert len(cell1.links) == 0
        assert len(cell2.links) == 1

        assert cell1 in cell2.links
        assert cell2 not in cell1.links

    def test_cell_unlink_bidirectional_alt(self):
        cell1 = Cell(5, 6)
        cell2 = Cell(2, 4)
        cell1.link(cell2)

        ## Unlink via Cell2 rather than Cell1
        cell2.unlink(cell1)

        assert len(cell1.links) == 0
        assert len(cell2.links) == 0

        assert cell1 not in cell2.links
        assert cell2 not in cell1.links

    def test_cell_is_linked(self):
        cell1 = Cell(5, 6)
        cell2 = Cell(2, 4)
        cell3 = Cell(1, 1)
        cell1.link(cell2)

        assert cell1.is_linked(cell2)
        assert cell2.is_linked(cell1)

        assert not cell1.is_linked(cell3)

    def test_cell_set_get_neighbors(self):
        cell = Cell(5, 6)
        cell_north = Cell(4, 6)
        cell_east = Cell(5, 6)
        cell_south = Cell(6, 5)
        cell_west = Cell(5, 5)

        cell.set_neighbor(Cell.NORTH, cell_north)
        assert cell.get_neighbor(Cell.NORTH) is cell_north

        with pytest.raises(NotImplementedError):
            assert cell.get_neighbor("foobar")

        assert cell.get_neighbor(Cell.SOUTH) is None

        cell.set_neighbor(Cell.EAST, cell_east)
        cell.set_neighbor(Cell.WEST, cell_west)
        cell.set_neighbor(Cell.SOUTH, cell_south)

        assert cell.get_neighbor(Cell.EAST) is cell_east
        assert cell.get_neighbor(Cell.WEST) is cell_west
        assert cell.get_neighbor(Cell.SOUTH) is cell_south

        neighbors = cell.neighbors()
        assert len(neighbors) == 4
        assert cell_north in neighbors
        assert cell_east in neighbors
        assert cell_south in neighbors
        assert cell_west in neighbors


    def test_cell_neighbors_alt(self):
        cell = Cell(5, 6)
        cell_north = Cell(4, 6)
        cell_east = Cell(5, 6)
        cell_south = Cell(6, 5)
        cell_west = Cell(5, 5)

        cell.set_neighbor(Cell.NORTH, cell_north)
        cell.set_neighbor(Cell.SOUTH, cell_south)
        cell.set_neighbor(Cell.EAST, cell_east)
        cell.set_neighbor(Cell.WEST, cell_west)

        assert cell.get_neighbor(Cell.NORTH) is cell_north
        assert cell.get_neighbor(Cell.EAST) is cell_east
        assert cell.get_neighbor(Cell.SOUTH) is cell_south
        assert cell.get_neighbor(Cell.WEST) is cell_west

        neighbors = cell.neighbors()
        assert len(neighbors) == 4
        assert cell_north in neighbors
        assert cell_east in neighbors
        assert cell_south in neighbors
        assert cell_west in neighbors

    def test_cell_neighbors_on_edge(self):
        cell = Cell(5, 6)
        ## No North neighbor
        cell_east = Cell(5, 6)
        cell_south = Cell(6, 5)
        cell_west = Cell(5, 5)

        cell.set_neighbor(Cell.SOUTH, cell_south)
        cell.set_neighbor(Cell.EAST, cell_east)
        cell.set_neighbor(Cell.WEST, cell_west)

        neighbors = cell.neighbors()
        assert len(neighbors) == 3
        assert cell_east in neighbors
        assert cell_south in neighbors
        assert cell_west in neighbors

    def test_cell_closest_neighbors(self):
        cell = Cell(5, 6)
        cell_north = Cell(4, 6)
        cell_east = Cell(5, 6)
        cell_south = Cell(6, 5)
        cell_west = Cell(5, 5)

        cell_north.distance = 1
        cell_east.distance = 2
        cell_west.distance = 2
        cell_south.distance = 5

        ## TODO: Decide if we want to assign this or not-- it kinda doesn't matter
        cell.north = cell_north
        cell.south = cell_south
        cell.east = cell_east
        cell.west = cell_west

        cell.link(cell_north, False)
        cell.link(cell_south, False)
        cell.link(cell_east, False)
        cell.link(cell_west, False)

        closest = cell.get_closest_cell()
        assert closest is cell_north

    def test_cell_closest_neighbors_no_neighbors(self):
        cell = Cell(5, 6)

        closest = cell.get_closest_cell()
        assert closest is None

class TestGrid:

    def test_grid_is_created(self):
        grid = Grid(3, 4)
        assert grid.num_rows == 3
        assert grid.num_cols == 4
        assert len(grid.rows) == 3
        assert len(grid.rows[0])== 4
        for row in grid.rows:
            assert len(row) == 4
            for cell in row:
                assert type(cell) is Cell
                if cell.row == 0:
                    assert cell.get_neighbor(Cell.NORTH) is None
                else:
                    assert cell.get_neighbor(Cell.NORTH) is not None
                if cell.row == 2:
                    assert cell.get_neighbor(Cell.SOUTH) is None
                else:
                    assert cell.get_neighbor(Cell.SOUTH) is not None
                if cell.col == 0:
                    assert cell.get_neighbor(Cell.WEST) is None
                else:
                    assert cell.get_neighbor(Cell.WEST) is not None
                if cell.col == 3:
                    assert cell.get_neighbor(Cell.EAST) is None
                else:
                    assert cell.get_neighbor(Cell.EAST) is not None
                north = cell.get_neighbor(Cell.NORTH)
                if north:
                    assert north.row == cell.row - 1
                    assert north.col == cell.col

                south = cell.get_neighbor(Cell.SOUTH)
                if south:
                    assert south.row == cell.row + 1
                    assert south.col == cell.col

                east = cell.get_neighbor(Cell.EAST)
                if east:
                    assert east.row == cell.row
                    assert east.col == cell.col + 1

                west = cell.get_neighbor(Cell.WEST)
                if west:
                    assert west.row == cell.row
                    assert west.col == cell.col - 1

    def test_grid_get_cell(self):
        grid = Grid(3, 4)
        for i in range(3):
            for j in range(4):
                cell = grid.get_cell(i, j)
                assert cell is not None
                assert cell.row == i
                assert cell.col == j
                if i == 0: ## First row
                    assert cell.get_neighbor(Cell.NORTH) is None
                if i == 2:
                    assert cell.get_neighbor(Cell.SOUTH) is None
                if j == 0:
                    assert cell.get_neighbor(Cell.WEST) is None
                if j == 3:
                    assert cell.get_neighbor(Cell.EAST) is None
                north = cell.get_neighbor(Cell.NORTH)
                if north:
                    assert north.row == i - 1
                    assert north.col == j

        assert grid.get_cell(-1, 2) is None
        assert grid.get_cell(5, 5) is None
        assert grid.get_cell(2, -1) is None

    def test_all_cells_list(self):
        grid = Grid(3, 4)
        cells = grid.all_cells()
        assert len(cells) == 12
        for cell in cells:
            assert cell.row >= 0
            assert cell.col >= 0
            assert cell.row < 3
            assert cell.col < 4


class TestBinaryTreeMazeMaker():
    def test_binary_tree_maze_maker(self):
        grid = Grid(12, 12)
        grid.print()
        maze = BinaryTreeMazeMaker(grid)
        grid.print()
        grid.export_image("binary_tree_maze.png")
        print("Review the image in images/binary_tree_maze.png")


class TestDjikstraSolver():
    def test_djikstra_solver(self):
        pass

    def test_relax(self):
        cell = Cell(5, 6)
        cell_north = Cell(4, 6)
        cell_east = Cell(5, 6)
        cell_south = Cell(6, 5)
        cell_west = Cell(5, 5)

        cell.set_neighbor(Cell.NORTH, cell_north)
        cell.set_neighbor(Cell.EAST, cell_east)
        cell.set_neighbor(Cell.WEST, cell_west)
        cell.set_neighbor(Cell.SOUTH, cell_south)

        cell.link(cell_north)
        cell.link(cell_east)

        cell.distance = 5
        cell_north.distance = 10 ## Should get updated
        cell_east.distance = 4 ## Should NOT get updated
        cell_south.distance = 3 ## Should not get updated-- not linked
        cell_west.distance = 2 ## Should not get updated-- cells aren't linked

        solver = DjikstraSolver(None)
        solver.relax(cell)

        assert cell_north.distance == 6
        assert cell_east.distance == 4
        assert cell_south.distance == 3
        assert cell_west.distance == 2

    def test_initialize(self):
        grid = Grid(3, 4)

        solver = DjikstraSolver(grid)
        solver.initialize()

        for index, cell in enumerate(grid):
            assert cell.distance == 10000



    def test_calculate_weight(self):
        solver = DjikstraSolver(None) ## Don't need an actual grid to test the weight() function
        cell1 = Cell(5, 6)
        cell2 = Cell(2, 4)
        cell3 = Cell(1, 0)

        cell1.link(cell2)

        assert solver.weight(cell1, cell2) == 1
        assert solver.weight(cell2, cell1) == 1

        assert solver.weight(cell1, cell3) == 10000
        assert solver.weight(cell3, cell2) == 10000

    def test_recover_path(self):
        grid = Grid(3, 4)
        c00 = grid.get_cell(0, 0)
        c01 = grid.get_cell(0, 1)
        c02 = grid.get_cell(0, 2)
        c03 = grid.get_cell(0, 3)
        c13 = grid.get_cell(1, 3)
        c23 = grid.get_cell(2, 3)
        ## If the cells aren't linked, there is no path
        c00.link(c01)
        c01.link(c02)
        c02.link(c03)
        c03.link(c13)
        c13.link(c23)

        ## Forcing the grid to have distances as follows:
        ## 0 1 2 3
        ## 1 4 3 4
        ## 1 2 3 5
        grid.get_cell(0, 0).distance = 0
        grid.get_cell(0, 1).distance = 1
        grid.get_cell(0, 2).distance = 2
        grid.get_cell(0, 3).distance = 3

        grid.get_cell(1, 0).distance = 1
        grid.get_cell(1, 1).distance = 4
        grid.get_cell(1, 2).distance = 3
        grid.get_cell(1, 3).distance = 4

        grid.get_cell(2, 0).distance = 1
        grid.get_cell(2, 1).distance = 2
        grid.get_cell(2, 2).distance = 3
        grid.get_cell(2, 3).distance = 5

        solver = DjikstraSolver(grid)
        path = solver.recover_path()
        print(path)
        assert path[0] is c00
        assert path[1] is c01
        assert path[2] is c02
        assert path[3] is c03
        assert path[4] is c13
        assert path[5] is c23

    def test_djikstra_no_solution(self):
        grid = Grid(10, 10)
        solver = DjikstraSolver(grid)
        path = solver.solve()
        assert len(path) == 0

    def test_djikstra_basic_aha(self):
        grid = Grid(3, 4)
        c00 = grid.get_cell(0, 0)
        c01 = grid.get_cell(0, 1)
        c02 = grid.get_cell(0, 2)
        c03 = grid.get_cell(0, 3)
        c13 = grid.get_cell(1, 3)
        c23 = grid.get_cell(2, 3)
        ## If the cells aren't linked, there is no path
        c00.link(c01)
        c01.link(c02)
        c02.link(c03)
        c03.link(c13)
        c13.link(c23)
        for ind, cell in enumerate(grid):
            cell.content = str(ind)
        grid.export_image("maze_djik.png")
        solver = DjikstraSolver(grid)
        path = solver.solve()
        for ind, cell in enumerate(grid):
            cell.content = cell.distance
        grid.export_image("maze_djik_solved.png")

        assert len(path) == 6
        assert path[0] is c00
        assert path[1] is c01
        assert path[2] is c02
        assert path[3] is c03
        assert path[4] is c13
        assert path[5] is c23
        grid.export_image("maze_basic_solved.png", path)

    def test_djikstra_basic(self):
        grid = Grid(10, 10)
        grid.print()
        maze = BinaryTreeMazeMaker(grid)
        grid.print()
        grid.export_image("maze_basic.png")
        solver = DjikstraSolver(grid)
        path = solver.solve()
        for ind, cell in enumerate(grid):
            cell.content = cell.distance
        print(path)
        grid.export_image("maze_basic_solved.png", path)


class TestOther:
    def test_first_content(self):
        grid = Grid(3, 4)
        for ind, cell in enumerate(grid):
            cell.content = ind
        grid.print()

        ## Test: right number

    def test_maze(self):
        grid = Grid(3, 4)
        grid.print()
        maze = BinaryTreeMazeMaker(grid)
        grid.print()

class TestSidewinder:

    def test_maze_sidewinder(self):
        grid = Grid(6, 6)
        grid.print()
        maze = SidewinderMazeMaker(grid)
        grid.print()
        ## Not a great way to test;
        ## Gonna just check that all cells have at least one linked neighbor
        for index, cell in enumerate(grid):
            assert len(cell.links) > 0

    def test_maze_sidewinder_image(self):
        ## This basically just exports an image so it can be viewed.
        grid = Grid(6, 6)
        grid.print()
        maze = SidewinderMazeMaker(grid)
        for ind, cell in enumerate(grid):
            cell.content = ind
        grid.print()
        grid.export_image()




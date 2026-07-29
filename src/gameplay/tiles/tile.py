from typing import override

from pygame import Surface
from pygame.draw import polygon
from pygamine import ImagePath
from pygamine import load_image

from pygamine import SpriteRenderer2D
from pygamine import GameObject


class Tile(GameObject):
	GRID_COLOR = (128, 128, 128)
	GRID_HOVER_COLOR = "yellow"
	HOVER_SHIFT_Y = 10

	def __init__(self, row_number, column_number):
		super().__init__()
		self.selected = False
		self.is_empty = True

		self.row_number, self.column_number = row_number, column_number
		renderer = self.add_component(SpriteRenderer2D)
		renderer.set_image(load_image(ImagePath("tile")))
		assert renderer.image is not None

		self.rect.size = renderer.image.get_size()
		self.rect.set_position(self.get_position(row_number, column_number))

		self.unselected_rect = self.rect.copy()
		self.selected_rect = self.rect.copy()
		self.selected_rect.y -= self.HOVER_SHIFT_Y

		self.surface = self.unselected_surface = renderer.image
		self.selected_surface = self.unselected_surface.__copy__()

		local_corners = [
			(0,                   (self.rect.height / 2) - 16),
			(self.rect.width / 2, 0),
			(self.rect.width,     (self.rect.height / 2) - 16),
			(self.rect.width / 2, self.rect.height - 34),
		]

		polygon(self.selected_surface, self.GRID_HOVER_COLOR, local_corners, 1)
		polygon(self.unselected_surface, self.GRID_COLOR, local_corners, 1)

		self.corners_of_unselected_polygon = [
			(x + self.rect.x, y + self.rect.y) for x, y in local_corners
		]
		self.corners_of_selected_polygon = [
			(x, y - self.HOVER_SHIFT_Y) for x, y in self.corners_of_unselected_polygon
		]

	@staticmethod
	def get_position(row, column) -> tuple:
		x = (column-row)*65 + 655 + 240
		y = (column+row)*32 + 200 + 90

		return x, y

	@staticmethod
	def get_area_of_triangle(points_of_triangle) -> float:
		x1, y1 = points_of_triangle[0]
		x2, y2 = points_of_triangle[1]
		x3, y3 = points_of_triangle[2]
		return abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1-y2))/2

	def is_point_in_triangle(self, points_of_triangle, point) -> bool:
		area_abc = self.get_area_of_triangle(points_of_triangle)
		area_apb = self.get_area_of_triangle([points_of_triangle[0], point, points_of_triangle[1]])
		area_apc = self.get_area_of_triangle([points_of_triangle[0], point, points_of_triangle[2]])
		area_bpc = self.get_area_of_triangle([points_of_triangle[1], point, points_of_triangle[2]])
		return abs(area_abc - (area_apb + area_apc + area_bpc)) < 0.5

	def is_point_in_quadrangle(self, points_of_quadrangle, point) -> bool:
		top = self.is_point_in_triangle([points_of_quadrangle[0], points_of_quadrangle[1], points_of_quadrangle[2]], point)
		bot = self.is_point_in_triangle([points_of_quadrangle[2], points_of_quadrangle[3], points_of_quadrangle[0]], point)
		return top or bot

	def is_mouse_over_selected(self, mouse_position) -> bool:
		return self.is_point_in_quadrangle(self.corners_of_selected_polygon, mouse_position)

	def is_mouse_over_unselected(self, mouse_position) -> bool:
		return self.is_point_in_quadrangle(self.corners_of_unselected_polygon, mouse_position)

	def is_mouse_over(self, mouse_position) -> bool:
		return self.is_mouse_over_selected(mouse_position) or self.is_mouse_over_unselected(mouse_position)

	@override
	def draw(self, window: Surface) -> None:
		if not self.active:
			return
		window.blit(self.selected_surface if self.selected else self.unselected_surface, self.rect)
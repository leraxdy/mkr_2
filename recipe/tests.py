from django.test import TestCase, Client
from django.urls import reverse

from .models import Category, Recipe


class MainViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Desserts')

    def test_main_view_status_code(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(response.status_code, 200)

    def test_main_view_uses_correct_template(self):
        response = self.client.get(reverse('main'))
        self.assertTemplateUsed(response, 'main.html')

    def test_main_view_returns_last_5_recipes(self):
        for i in range(7):
            Recipe.objects.create(
                title=f'Recipe {i}',
                description='desc',
                instructions='instr',
                ingredients='ingr',
                category=self.category,
            )
        response = self.client.get(reverse('main'))
        self.assertEqual(len(response.context['recipes']), 5)

    def test_main_view_recipes_ordered_by_newest(self):
        for i in range(3):
            Recipe.objects.create(
                title=f'Recipe {i}',
                description='desc',
                instructions='instr',
                ingredients='ingr',
                category=self.category,
            )
        response = self.client.get(reverse('main'))
        recipes = list(response.context['recipes'])
        dates = [r.created_at for r in recipes]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_main_view_no_recipes(self):
        response = self.client.get(reverse('main'))
        self.assertEqual(len(response.context['recipes']), 0)
        self.assertContains(response, 'No recipes found.')

    def test_main_view_recipes_context_key(self):
        response = self.client.get(reverse('main'))
        self.assertIn('recipes', response.context)


class CategoryListViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_category_list_view_status_code(self):
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)

    def test_category_list_view_uses_correct_template(self):
        response = self.client.get(reverse('category_list'))
        self.assertTemplateUsed(response, 'category_list.html')

    def test_category_list_view_returns_all_categories(self):
        Category.objects.create(name='Desserts')
        Category.objects.create(name='Soups')
        Category.objects.create(name='Salads')
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.context['categories'].count(), 3)

    def test_category_list_view_recipe_count_annotation(self):
        cat = Category.objects.create(name='Desserts')
        Recipe.objects.create(
            title='Cake', description='d', instructions='i',
            ingredients='i', category=cat,
        )
        Recipe.objects.create(
            title='Cookie', description='d', instructions='i',
            ingredients='i', category=cat,
        )
        response = self.client.get(reverse('category_list'))
        category = response.context['categories'].get(name='Desserts')
        self.assertEqual(category.recipe_count, 2)

    def test_category_list_view_empty_category_has_zero_recipes(self):
        Category.objects.create(name='Empty Category')
        response = self.client.get(reverse('category_list'))
        category = response.context['categories'].get(name='Empty Category')
        self.assertEqual(category.recipe_count, 0)

    def test_category_list_view_no_categories(self):
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.context['categories'].count(), 0)
        self.assertContains(response, 'No categories found.')

    def test_category_list_view_context_key(self):
        response = self.client.get(reverse('category_list'))
        self.assertIn('categories', response.context)

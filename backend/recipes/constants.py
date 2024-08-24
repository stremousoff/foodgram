class Config:
    # Кол-во показываемых символов методом __str__()
    LENGTH_ON_STR = 15

    # Настройки моделей
    INGREDIENT_MAX_LENGTH = 128
    MEASUREMENT_MAX_LENGTH = 64
    TAG_MAX_LENGTH = 32
    SLUG_MAX_LENGTH = 32
    DIRECTORY_RECIPE = 'recipes/'
    MIN_COOKING_TIME = 1
    MAX_COOKING_TIME = 32767
    MAX_URL_LENGTH = 4
    NAME_RECIPE_MAX_LENGTH = 256
    MIN_INGREDIENT_AMOUNT = 1
    MAX_INGREDIENT_AMOUNT = 32767

    # Verbose name
    NAME_INGREDIENT = 'Названия ингредиента'
    MEASUREMENT_UNIT = 'Единица измерения'
    NAME_TAG = 'Тэг'
    SLUG_TAG = 'Слаг'
    AUTHOR = 'Автор'
    NAME_RECIPE = 'Название рецепта'
    IMAGE_RECIPE = 'Изображение рецепта'
    TEXT_RECIPE = 'Описание рецепта'
    COOKING_TIME = 'Время приготовления'
    SHORT_URL = 'Короткая ссылка на рецепт'
    ADD_TIME = 'Время добавления рецепта на сайт'
    AMOUNT = 'Количество ингредиента в рецепте'
    USER = 'Пользователь'

    # Verbose/plural для META
    INGREDIENT = 'Ингредиент'
    INGREDIENTS = 'Ингредиенты'
    TAG = 'Тег'
    TAGS = 'Теги'
    RECIPE = 'Рецепт'
    RECIPES = 'Рецепты'
    INGREDIENT_RECIPE = 'Ингредиенты рецепта'
    INGREDIENTS_RECIPE = 'Ингредиенты для рецепта'
    FAVORITED_RECIPE = 'Понравившейся пользователю рецепт'
    FAVORITED_RECIPES = 'Понравившиеся пользователю рецепты'
    SHOPPING_CART = 'Список покупок'

    # Errors
    MIN_COOKING_TIME_ERROR = (f'Время приготовления должно быть не менее '
                              f'{MIN_COOKING_TIME}!')
    MAX_COOKING_TIME_ERROR = (f'Время приготовления должно быть не более '
                              f'{MAX_COOKING_TIME}!')
    MIN_INGREDIENT_AMOUNT_ERROR = (f'Количество ингредиента должно быть не '
                                   f'менее {MIN_INGREDIENT_AMOUNT}!')
    MAX_INGREDIENT_AMOUNT_ERROR = (f'Количество ингредиента должно быть не '
                                   f'более {MAX_INGREDIENT_AMOUNT}')

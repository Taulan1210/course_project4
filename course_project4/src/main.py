from src.class_api import HeadHunterRuAPI
from src.class_connector import SaveJson
from src.class_vacancies_hh import VacanciesHH
import json


def get_value(dictionary, *keys):
    """
    Возвращает значение из словаря по заданному пути ключей
    :param dictionary: словарь, из которого мы получаем значение
    :param keys: переменное количество ключей в виде строки, определяющих путь к значению.
    :return: Значение из словаря, связанное с заданным путем ключей.
     Если хотя бы один ключ не существует или путь прерывается значениями None, будет возвращено None.
    """
    for key in keys:
        if dictionary is None:
            return None
        dictionary = dictionary.get(key)
    return dictionary


def user_interaction():
    print('''Привет! С помощью этого приложения поиск вакансий на Hh.ru станет намного проще.
          Вот несколько рекомендаций для комфортного взаимодействия с программой:
          Количество вакансий указывать только цифрами, иначе будут выданы все найденные по имени вакансии
          ----
          Ключевые слова нужно разделять пробелами
          ----
          Если не будет найдено ни одного совпадения по ключевым словам,
          то программа выдаст количество вакансий, указанных в следующем вводе
          ----''')
    name_vacancy = input('Введите название вакансии: ')
    keyword_vacancy = input('Введите ключевые слова для фильтрации вакансий: ').split()

    try:
        top_n = int(input('Введите количество вакансий для отображения по убыванию зарплаты: '))
        if top_n <= 0:
            raise ValueError
    except ValueError:
        print('Получено некорректное значение. Будут выданы все результаты:')
        top_n = None

    vacancy_hh = HeadHunterRuAPI()
    all_vacancy = vacancy_hh.getting_vacancies(name_vacancy)

    # Фильтрация вакансий по валюте RUR (т.к ищем в России)
    all_vacancy = [vacancy for vacancy in all_vacancy.get('items') if get_value(vacancy, 'salary', 'currency') == 'RUR']

    if len(all_vacancy) == 0:
        print("По вашему запросу вакансий не найдено")
    else:
        print(f"Всего количество вакансий по запросу '{name_vacancy}': {len(all_vacancy)}")
        print(f"Топ {top_n or len(all_vacancy)} вакансий по зарплате:")

        good_vacancy = []

        if not keyword_vacancy:
            top_n_vacancy = top_n or len(all_vacancy)
            for vacancy in all_vacancy[:top_n_vacancy]:
                try:
                    name = get_value(vacancy, 'name')
                    area = get_value(vacancy, 'area', 'name')
                    salary_from = get_value(vacancy, 'salary', 'from')
                    salary_to = get_value(vacancy, 'salary', 'to')
                    salary_currency = get_value(vacancy, 'salary', 'currency')
                    requirement = get_value(vacancy, 'snippet', 'requirement')
                    alternate_url = get_value(vacancy, 'alternate_url')
                    good_vacancy.append(
                        VacanciesHH(name, area, salary_from, salary_to, salary_currency, requirement, alternate_url))
                except Exception as e:
                    print(f"Ошибка обработки вакансии: {e}")
        else:
            for vacancy in all_vacancy:
                try:
                    name = get_value(vacancy, 'name')
                    area = get_value(vacancy, 'area', 'name')
                    salary_from = get_value(vacancy, 'salary', 'from')
                    salary_to = get_value(vacancy, 'salary', 'to')
                    salary_currency = get_value(vacancy, 'salary', 'currency')
                    requirement = get_value(vacancy, 'snippet', 'requirement')
                    alternate_url = get_value(vacancy, 'alternate_url')
                    if any(keyword.lower() in str(vacancy).lower() for keyword in keyword_vacancy):
                        good_vacancy.append(
                            VacanciesHH(name, area, salary_from, salary_to, salary_currency, requirement,
                                        alternate_url))
                except Exception as e:
                    print(f"Ошибка обработки вакансии: {e}")

        if len(good_vacancy) == 0:
            top_n_vacancy = top_n or len(all_vacancy)
            print(f"Ключевые слова не найдены. Будут выданы все результаты: {top_n_vacancy} вакансий.")
            good_vacancy = all_vacancy[:top_n_vacancy]
        else:
            top_vacancy = sorted(good_vacancy, key=lambda x: x.salary_to if x.salary_to is not None else 0,
                                 reverse=True)
            good_vacancy = top_vacancy[:top_n]

        for vacancy in good_vacancy:
            print(vacancy)

    with open('/Users/andalou/PycharmProjects/API-hh/data/vacancies.json', 'w') as file:
        json.dump(good_vacancy, file, default=lambda x: x.__dict__)  # записывает в файл vacancies.json выбранные пользователем вакансии


if __name__ == "__main__":
    user_interaction()

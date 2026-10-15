@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "AI-агент" as AI
actor "RAG «Продукты и цены»" as RAG
actor "БД «Мои продукты»" as LocalDB
actor "БД профилей" as ProfileDB
actor "CV Модель" as CV

rectangle "AI Планировщик питания" {
  
  usecase "UC-1. Настроить профиль" as UC1
  usecase "UC-2. Пополнить базу\n«Мои продукты»" as UC2
  usecase "UC-3. Сгенерировать\nменю" as UC3
  usecase "UC-4. Заменить блюдо" as UC4
  usecase "UC-5. Перенести блюдо" as UC5
  usecase "UC-6. Сгенерировать рецепт\nиз остатков" as UC6
  usecase "UC-7. Сгенерировать\nбыстрый ужин" as UC7
  usecase "UC-8. Рассчитать КБЖУ\nпо фото" as UC8
  usecase "UC-9. Выбрать блюдо\nиз «Коллекций»" as UC9

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC1
User --> UC2
User --> UC3
User --> UC4
User --> UC5
User --> UC6
User --> UC7
User --> UC8
User --> UC9

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-1: Настройка профиля
UC1 ..> ProfileDB : <<include>>\nСохранить ограничения

' UC-2: Пополнение локальной базы «Мои продукты»
UC2 ..> RAG : <<include>>\nПолучить срок годности
UC2 ..> LocalDB : <<include>>\nСохранить в локальную БД

' UC-3: Генерация персонализированного меню
UC3 ..> AI : <<include>>\nСгенерировать план
UC3 ..> RAG : <<include>>\nПосчитать цены и КБЖУ
UC3 ..> LocalDB : <<include>>\nУчесть имеющиеся продукты
UC3 ..> ProfileDB : <<include>>\nПолучить ограничения

' UC-4: Замена блюда
UC4 ..> AI : <<include>>\nНайти альтернативу
UC4 ..> RAG : <<include>>\nПосчитать цены и КБЖУ
UC4 ..> ProfileDB : <<include>>\nПолучить ограничения

' UC-5: Каскадный перенос меню
UC5 ..> RAG : <<include>>\nПосчитать цены и КБЖУ

' UC-6: Сгенерировать Zero-Waste рецепт
UC6 ..> AI : <<include>>\nСгенерировать рецепт
UC6 ..> LocalDB : <<include>>\nПолучить список продуктов-остатков
UC6 ..> ProfileDB : <<include>>\nПолучить ограничения

' UC-7: Сгенерировать Быстрый ужин
UC7 ..> AI : <<include>>\nСгенерировать рецепт
UC7 ..> LocalDB : <<include>>\nПолучить список продуктов-остатков
UC7 ..> ProfileDB : <<include>>\nПолучить ограничения

' UC-8: Оценка КБЖУ по фото
UC8 ..> CV : <<include>>\nПроанализировать изображение
UC8 ..> RAG : <<include>>\nПосчитать цены и КБЖУ

' UC-9: Выбор блюда из раздела «Коллекции»
UC9 ..> RAG : <<include>>\nПолучить базу рецептов
UC9 ..> ProfileDB : <<include>>\nПолучить ограничения

@enduml
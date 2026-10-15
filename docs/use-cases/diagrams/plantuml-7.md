@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "AI-агент" as AI

actor "БД «Мои продукты»" as LocalDB

rectangle "AI Планировщик питания" {
  
  usecase "UC-7. Сгенерировать\nбыстрый ужин" as UC7

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC7

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-7: Сгенерировать Быстрый ужин
UC7 ..> AI : <<include>>\nСгенерировать рецепт
UC7 ..> LocalDB : <<include>>\nПолучить список продуктов-остатков
UC7 ..> ProfileDB : <<include>>\nПолучить ограничения

@enduml
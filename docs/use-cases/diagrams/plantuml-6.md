@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "AI-агент" as AI
actor "БД «Мои продукты»" as LocalDB
actor "БД профилей" as ProfileDB

rectangle "AI Планировщик питания" {
  
  usecase "UC-6. Сгенерировать рецепт\nиз остатков" as UC6

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC6

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-6: Сгенерировать Zero-Waste рецепт
UC6 ..> AI : <<include>>\nСгенерировать рецепт
UC6 ..> LocalDB : <<include>>\nПолучить список продуктов-остатков
UC6 ..> ProfileDB : <<include>>\nПолучить ограничения

@enduml
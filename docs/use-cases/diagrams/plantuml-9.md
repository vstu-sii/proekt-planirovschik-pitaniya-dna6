@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "RAG «Продукты и цены»" as RAG
actor "БД профилей" as ProfileDB

rectangle "AI Планировщик питания" {
  
  usecase "UC-9. Выбрать блюдо\nиз «Коллекций»" as UC9

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC9

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-9: Выбор блюда из раздела «Коллекции»
UC9 ..> RAG : <<include>>\nПолучить базу рецептов
UC9 ..> ProfileDB : <<include>>\nПолучить ограничения

@enduml
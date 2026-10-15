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

rectangle "AI Планировщик питания" {
  
  usecase "UC-3. Сгенерировать\nменю" as UC3

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC3

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-3: Генерация персонализированного меню
UC3 ..> AI : <<include>>\nСгенерировать план
UC3 ..> RAG : <<include>>\nПосчитать цены и КБЖУ
UC3 ..> LocalDB : <<include>>\nУчесть имеющиеся продукты
UC3 ..> ProfileDB : <<include>>\nПолучить ограничения

@enduml
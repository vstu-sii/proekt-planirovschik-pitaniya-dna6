@startuml
left to right direction
skinparam packageStyle rectangle
skinparam monochrome true
skinparam shadowing false

actor "Пользователь" as User
actor "AI-агент" as AI
actor "RAG «Продукты и цены»" as RAG
actor "БД профилей" as ProfileDB

rectangle "AI Планировщик питания" {

  usecase "UC-4. Заменить блюдо" as UC4

}

' СВЯЗИ ПОЛЬЗОВАТЕЛЯ С СИСТЕМОЙ
User --> UC4

' ВЗАИМОДЕЙСТВИЯ СИСТЕМЫ

' UC-4: Замена блюда
UC4 ..> AI : <<include>>\nНайти альтернативу
UC4 ..> RAG : <<include>>\nПосчитать цены и КБЖУ
UC4 ..> ProfileDB : <<include>>\nПолучить ограничения

@enduml